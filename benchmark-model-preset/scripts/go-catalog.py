#!/usr/bin/env python3
"""Parse the OpenCode Go model catalog from https://opencode.ai/docs/go/.

The docs page carries every number this parser needs in plain server-rendered
HTML: model ids, endpoints, AI SDK packages, per-plan price tables, estimated
request tables and the training/retention table. No JS, no special headers, no
browser. This script is the durable replacement for the throwaway inline parser
the agent used to retype.

Tables found on the page (Oct 19, 2026 layout):

  * plan prices       Plan | Price | Included usage
  * client support    Client | Session support  (ignored, not catalog data)
  * Go pricing        Model | Input | Output | Cached Read | Cached Write | Monthly limit
  * Go Plus pricing   same shape, wrapped in <div data-plan-panel="go-plus">
  * Go requests       Model | Requests per 5 hours | Requests per week | Requests per month
  * Go Plus requests  same shape, second plan panel
  * catalog           Model | Model ID | Endpoint | AI SDK Package
  * privacy           Model | Model training | Data retention

Cells use <del> for the pre-promotion value, <strong> for the current value and
<small> for notes such as "4x / Limited time". The parser reads those tags, so
it reports the current number and keeps the struck one in the notes.

Display names in the pricing/requests/privacy tables are not ids. They are
folded to a join key by dropping parentheticals and case: "Qwen3.7 Plus
(<= 256K tokens)" -> "qwen3.7 plus"; the catalog table supplies the real id.

Usage:
    ./go-catalog.py                 # JSON (default)
    ./go-catalog.py --table         # human table
    ./go-catalog.py --ids           # ids, one per line, page order
    ./go-catalog.py --ids-for-plan go_plus
    ./go-catalog.py --plan go --table
    ./go-catalog.py --offline       # parse the cache, fail if missing
    ./go-catalog.py --refresh       # force a fetch

Cache: scripts/out/go-docs.html (override with --cache). A run reuses the cache
when it is younger than --max-age (default 3600s) and refetches otherwise.

Every unparsable row is skipped, quoted on stderr and counted; the final stderr
line is always `skipped_rows: N`.

Exit codes: 0 ok, 1 cache missing under --offline / fetch failed, 2 bad args.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import html as _html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser

SOURCE_URL = "https://opencode.ai/docs/go/"
DEFAULT_CACHE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "out", "go-docs.html"
)
MODELS_DEV_URL = "https://models.dev/api.json"
MODELS_DEV_CACHE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "out", "models-dev.json"
)
DEFAULT_MAX_AGE = 3600
USER_AGENT = "go-catalog.py (+https://opencode.ai/docs/go/)"

MODEL_ID_RE = re.compile(r"^[a-z0-9][a-z0-9.\-]*$")
PAREN_RE = re.compile(r"\s*\([^()]*\)")
PROMO_RE = re.compile(r"(\d+)\s*x\s*(?:\u00b7|\.)?\s*limited time", re.I)
LIMITED_RE = re.compile(r"limited time", re.I)
STRONG_LEAD_RE = re.compile(r"^<strong>(.+?)(?::?)</strong>\s*:?\s*(.*)$", re.S)

PLANS = ("go", "go_plus")


# --------------------------------------------------------------------------
# tiny HTML table reader
# --------------------------------------------------------------------------


class _Cell:
    __slots__ = ("text", "main", "strong", "del_", "small")

    def __init__(self) -> None:
        self.text: list[str] = []
        self.main: list[str] = []
        self.strong: list[str] = []
        self.del_: list[str] = []
        self.small: list[str] = []

    def plain(self) -> str:
        return _norm("".join(self.text))

    def main_plain(self) -> str:
        return _norm("".join(self.main))

    def strong_plain(self) -> str:
        return _norm("".join(self.strong))

    def del_plain(self) -> str:
        return _norm("".join(self.del_))

    def small_plain(self) -> str:
        return _norm("".join(self.small))


def _norm(value: str) -> str:
    return re.sub(r"\s+", " ", _html.unescape(value)).strip()


class TableReader(HTMLParser):
    """Collect tables plus the `data-plan-panel` each table sits inside."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[dict] = []
        self._table_stack: list[dict] = []
        self._row: dict | None = None
        self._cell: _Cell | None = None
        self._special: list[tuple[str, list[str]]] = []
        self._div_depth = 0
        self._panels: list[tuple[int, str]] = []
        self._plan: str | None = None

    # -- start tags ------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        if tag == "div":
            self._start_div(attrs)
        elif tag == "table":
            self._start_table()
        elif tag == "tr":
            self._start_row()
        elif tag in ("td", "th"):
            self._start_cell()
        elif tag == "br":
            self._feed(" ")
        elif tag in ("del", "s", "strike", "strong", "small"):
            self._open_special(tag)

    def handle_startendtag(self, tag, attrs):
        if tag == "br":
            self._feed(" ")

    def _start_div(self, attrs):
        self._div_depth += 1
        panel = dict(attrs).get("data-plan-panel")
        if panel:
            self._panels.append((self._div_depth, panel))
            self._plan = panel

    def _start_table(self):
        table = {"rows": [], "plan": self._plan}
        self.tables.append(table)
        self._table_stack.append(table)

    def _start_row(self):
        if self._table_stack:
            self._row = {"cells": []}

    def _start_cell(self):
        if self._row is not None:
            self._cell = _Cell()

    def _open_special(self, tag):
        if self._cell is None:
            return
        if tag == "strong":
            self._special.append(("strong", self._cell.strong))
        elif tag == "small":
            self._special.append(("small", self._cell.small))

    # -- end tags --------------------------------------------------------
    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self._close_cell()
        elif tag == "tr":
            self._close_row()
        elif tag == "table":
            self._close_table()
        elif tag == "div":
            self._close_div()
        elif tag in ("del", "s", "strike", "strong", "small"):
            self._close_special(tag)

    def _close_cell(self):
        if self._cell is not None and self._row is not None:
            self._row["cells"].append(self._cell)
        self._cell = None
        self._special.clear()

    def _close_row(self):
        if self._row is not None and self._table_stack:
            self._table_stack[-1]["rows"].append(self._row)
        self._row = None
        self._cell = None

    def _close_table(self):
        if self._table_stack:
            self._table_stack.pop()
        self._row = None
        self._cell = None

    def _close_special(self, tag):
        for index in range(len(self._special) - 1, -1, -1):
            if self._special[index][0] == tag:
                del self._special[index]
                return

    def _close_div(self):
        while self._panels and self._panels[-1][0] == self._div_depth:
            self._panels.pop()
        self._div_depth = max(0, self._div_depth - 1)
        self._plan = self._panels[-1][1] if self._panels else None

    # -- text ------------------------------------------------------------
    def handle_data(self, data):
        if self._cell is not None:
            self._feed(data)

    def _feed(self, data: str) -> None:
        if self._cell is None:
            return
        self._cell.text.append(data)
        active = {tag for tag, _ in self._special}
        if "small" not in active and "del" not in active:
            self._cell.main.append(data)
        for _, buffer in self._special:
            buffer.append(data)


# --------------------------------------------------------------------------
# scalar parsing
# --------------------------------------------------------------------------


def fold(name: str) -> str:
    """Join key: drop parentheticals, casefold, collapse space."""
    out = PAREN_RE.sub(" ", name)
    out = out.replace("\u2264", " ").replace("\u2265", " ")
    out = re.sub(r"\s+", " ", out).strip().lower()
    return out


def _number(raw: str):
    cleaned = raw.strip().lstrip("$").replace(",", "").replace("*", "").strip()
    if not cleaned:
        return None
    try:
        value = float(cleaned)
    except ValueError:
        return None
    return int(value) if value.is_integer() else value


def money(raw: str) -> dict:
    raw = (raw or "").strip() or "-"
    low = raw.lower()
    if low == "free":
        return {"raw": raw, "value": 0.0, "unlimited": False, "free": True}
    if low in ("-", "\u2014"):
        return {"raw": "-", "value": None, "unlimited": False, "free": False}
    if low == "unlimited":
        return {"raw": raw, "value": None, "unlimited": True, "free": False}
    return {"raw": raw, "value": _number(raw), "unlimited": False, "free": False}


def count(raw: str) -> dict:
    raw = (raw or "").strip() or "-"
    if raw.lower() == "unlimited":
        return {"raw": raw, "value": None, "unlimited": True}
    return {"raw": raw, "value": _number(raw), "unlimited": False}


def pick(cell: _Cell) -> str:
    """Current value: the <strong> text when the page renders a promotion."""
    return cell.strong_plain() or cell.main_plain() or cell.plain()


# --------------------------------------------------------------------------
# fetch / cache
# --------------------------------------------------------------------------


def _stamp(ts: float) -> str:
    return _dt.datetime.fromtimestamp(ts, _dt.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def _read_cache(path: str, meta: dict, label: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        body = handle.read()
    meta.update(source="cache")
    print(f"cache: {path} ({label})", file=sys.stderr)
    return body


def _fetch(path: str, timeout: float) -> str:
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        sys.exit(f"error: fetch failed for {SOURCE_URL}: {exc}")


def load_html(args) -> tuple[str, dict]:
    path = os.path.abspath(args.cache)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    exists = os.path.isfile(path)
    age = time.time() - os.path.getmtime(path) if exists else None
    meta = {"cache": path}

    if args.offline:
        if not exists:
            sys.exit(f"error: --offline but cache is missing: {path}")
        meta["fetched_at"] = _stamp(os.path.getmtime(path))
        return _read_cache(path, meta, f"offline, age {int(age)}s"), meta

    if exists and not args.refresh and age is not None and age <= args.max_age:
        meta["fetched_at"] = _stamp(os.path.getmtime(path))
        return _read_cache(
            path, meta, f"age {int(age)}s, reused; --refresh to refetch"
        ), meta

    body = _fetch(path, args.timeout)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        handle.write(body)
    os.replace(tmp, path)
    fetched = time.time()
    meta.update(source="network", fetched_at=_stamp(fetched), bytes=len(body))
    print(
        f"cache: {path} (fetched {_stamp(fetched)}, {len(body)} bytes)", file=sys.stderr
    )
    return body, meta


# --------------------------------------------------------------------------
# prose
# --------------------------------------------------------------------------


def _strip_tags(fragment: str) -> str:
    return _norm(re.sub(r"<[^>]+>", " ", fragment))


def _regions_from(text: str) -> list[str]:
    split = re.split(r"not available in\s+", text, flags=re.I)
    if len(split) < 2:
        return []
    tail = split[1].rstrip(".")
    parts = re.split(r",\s*(?:or\s+|and\s+)?|\s+or\s+", tail)
    return [
        re.sub(r"^(?:and|or)\s+", "", part).strip()
        for part in parts
        if re.sub(r"^(?:and|or)\s+", "", part).strip()
    ]


def parse_prose(raw_html: str) -> tuple[list[dict], list[str]]:
    """Model-scoped notes and region exclusions from the article <p> blocks."""
    notes: list[dict] = []
    regions: list[str] = []
    for match in re.finditer(r"<p>(.*?)</p>", raw_html, re.S):
        lead = STRONG_LEAD_RE.match(match.group(1))
        if not lead:
            continue
        names = [_strip_tags(name).rstrip(":") for name in lead.group(1).split("/")]
        body = _strip_tags(lead.group(2))
        if not body:
            continue
        for name in names:
            if name:
                notes.append({"model": name, "text": body})
        regions.extend(_regions_from(body))
    return notes, regions


# --------------------------------------------------------------------------
# table readers
# --------------------------------------------------------------------------


def _empty_plan_info() -> dict:
    return {
        key: {
            "name": "Go Plus" if key == "go_plus" else "Go",
            "price": money("-"),
            "included": None,
        }
        for key in PLANS
    }


def _new_context() -> dict:
    return {
        "catalog": [],
        "pricing": {key: {} for key in PLANS},
        "requests": {key: {} for key in PLANS},
        "privacy": {},
        "plan_info": _empty_plan_info(),
    }


_TABLE_RULES = (
    (lambda header: "plan" in header and "price" in header, "plan_prices"),
    (lambda header: header[:1] == ["model"] and "monthly limit" in header, "pricing"),
    (
        lambda header: (
            header[:1] == ["model"] and any("requests per" in item for item in header)
        ),
        "requests",
    ),
    (lambda header: "model id" in header, "catalog"),
    (lambda header: "model training" in header, "privacy"),
)


def _table_kind(header: list[str]) -> str | None:
    for matches, kind in _TABLE_RULES:
        if matches(header):
            return kind
    return None


def _plan_key(value: str | None) -> str | None:
    return value.replace("-", "_") if value else None


def plan_price(raw: str) -> dict:
    """'$10/month' -> raw kept, value 10."""
    entry = money(raw)
    if entry["value"] is None:
        found = re.search(r"[0-9]+(?:\.[0-9]+)?", entry["raw"])
        if found:
            value = float(found.group(0))
            entry["value"] = int(value) if value.is_integer() else value
    return entry


def _read_plan_prices(rows, table, ctx, skipped):
    for row in rows:
        cells = row["cells"]
        if len(cells) < 2:
            skipped.append("plan: " + _row_text(cells))
            continue
        name = cells[0].plain()
        key = "go_plus" if name.lower().startswith("go plus") else "go"
        ctx["plan_info"][key] = {
            "name": name,
            "price": plan_price(pick(cells[1])),
            "included": cells[2].plain() if len(cells) > 2 else None,
        }


def _read_pricing(rows, table, ctx, skipped):
    plan = _plan_key(table["plan"])
    if plan not in PLANS:
        skipped.append(
            "pricing without plan panel: " + _row_text(rows[0]["cells"])
            if rows
            else "pricing"
        )
        return
    for row in rows:
        cells = row["cells"]
        key = fold(cells[0].plain()) if cells else ""
        if len(cells) < 6 or not key:
            skipped.append(f"pricing[{plan}]: " + _row_text(cells))
            continue
        limit = cells[5]
        ctx["pricing"][plan].setdefault(key, []).append(
            {
                "label": cells[0].plain(),
                "input": money(pick(cells[1])),
                "output": money(pick(cells[2])),
                "cache_read": money(pick(cells[3])),
                "cache_write": money(pick(cells[4])),
                "monthly_limit": money(pick(limit)),
                "monthly_limit_struck": limit.del_plain() or None,
                "note": limit.small_plain() or None,
            }
        )


def _read_requests(rows, table, ctx, skipped):
    plan = _plan_key(table["plan"])
    if plan not in PLANS:
        skipped.append(
            "requests without plan panel: "
            + (_row_text(rows[0]["cells"]) if rows else "")
        )
        return
    for row in rows:
        cells = row["cells"]
        label = cells[0].main_plain() or cells[0].plain() if cells else ""
        key = fold(label)
        if len(cells) < 4 or not key:
            skipped.append(f"requests[{plan}]: " + _row_text(cells))
            continue
        ctx["requests"][plan][key] = {
            "label": label,
            "five_hour": count(pick(cells[1])),
            "week": count(pick(cells[2])),
            "month": count(pick(cells[3])),
            "note": cells[0].small_plain() or None,
        }


def _read_catalog(rows, table, ctx, skipped):
    header = [c.plain().lower() for c in table["rows"][0]["cells"]]
    id_col = header.index("model id")
    endpoint_col = header.index("endpoint") if "endpoint" in header else None
    sdk_col = header.index("ai sdk package") if "ai sdk package" in header else None
    for row in rows:
        cells = row["cells"]
        model_id = cells[id_col].plain() if len(cells) > id_col else ""
        if not MODEL_ID_RE.match(model_id):
            skipped.append("catalog(row has no id): " + _row_text(cells))
            continue
        ctx["catalog"].append(
            {
                "id": model_id,
                "display": cells[0].main_plain() or cells[0].plain(),
                "endpoint": cells[endpoint_col].plain()
                if endpoint_col is not None
                else None,
                "sdk": cells[sdk_col].plain() if sdk_col is not None else None,
            }
        )


def _read_privacy(rows, table, ctx, skipped):
    for row in rows:
        cells = row["cells"]
        key = fold(cells[0].plain()) if cells else ""
        if len(cells) < 3 or not key:
            skipped.append("privacy: " + _row_text(cells))
            continue
        ctx["privacy"][key] = {
            "label": cells[0].plain(),
            "training": cells[1].plain(),
            "retention": cells[2].plain(),
        }


READERS = {
    "plan_prices": _read_plan_prices,
    "pricing": _read_pricing,
    "requests": _read_requests,
    "catalog": _read_catalog,
    "privacy": _read_privacy,
}


def _row_text(cells) -> str:
    return " | ".join(cell.plain() for cell in cells)


def _consume_table(table: dict, ctx: dict, skipped: list[str]) -> None:
    rows = table["rows"]
    if not rows or not rows[0]["cells"]:
        return
    header = [cell.plain().lower() for cell in rows[0]["cells"]]
    reader = READERS.get(_table_kind(header))
    if reader is None:
        return
    reader([row for row in rows[1:] if row["cells"]], table, ctx, skipped)


# --------------------------------------------------------------------------
# model assembly
# --------------------------------------------------------------------------


def _primary_price(ctx: dict, plan: str, key: str) -> dict | None:
    rows = ctx["pricing"][plan].get(key, [])
    return rows[0] if rows else None


def _flags(
    price: dict, cell_notes: list[str], notes: list[str]
) -> tuple[bool, bool, str | None]:
    free = bool(price["input"].get("free") or price["output"].get("free"))
    promo = None
    for text in cell_notes + notes:
        found = PROMO_RE.search(text)
        if found:
            promo = f"{found.group(1)}x"
            break
    limited = bool(promo) or any(LIMITED_RE.search(text) for text in cell_notes + notes)
    return free, limited, promo


def _plan_block(price: dict | None, requests: dict | None) -> dict:
    if price is None:
        return {
            "price": None,
            "monthly_limit": None,
            "monthly_limit_struck": None,
            "requests": None,
            "listed": False,
        }
    return {
        "price": {
            "input": price["input"],
            "output": price["output"],
            "cache_read": price["cache_read"],
            "cache_write": price["cache_write"],
            "monthly_limit": price["monthly_limit"],
        },
        "monthly_limit": price["monthly_limit"],
        "monthly_limit_struck": price["monthly_limit_struck"],
        "requests": None
        if requests is None
        else {
            "five_hour": requests["five_hour"],
            "week": requests["week"],
            "month": requests["month"],
        },
        "listed": True,
    }


def _build_model(
    entry: dict, ctx: dict, notes_by_key: dict, region_keys: set
) -> dict | None:
    key = fold(entry["display"])
    go_price = _primary_price(ctx, "go", key)
    if go_price is None:
        return None
    plus_price = _primary_price(ctx, "go_plus", key) or go_price
    go_req = ctx["requests"]["go"].get(key)
    plus_req = ctx["requests"]["go_plus"].get(key)
    privacy = ctx["privacy"].get(key) or {}

    variants = [row["label"] for row in ctx["pricing"]["go"].get(key, [])[1:]]
    cell_notes = [
        row["note"] for row in ctx["pricing"]["go"].get(key, []) if row["note"]
    ]
    model_notes = list(notes_by_key.get(key, []))
    if variants and not any("variants" in note for note in model_notes):
        model_notes.insert(0, "Go price variants: " + "; ".join(variants))
    free, limited, promo = _flags(go_price, cell_notes, model_notes)
    struck = go_price["monthly_limit_struck"]
    if struck:
        suffix = f" ({promo})" if promo else ""
        model_notes.append(
            f"monthly limit {struck} -> {go_price['monthly_limit']['raw']}{suffix}"
        )
    if promo and not any("limited time" in note.lower() for note in model_notes):
        model_notes.append(f"{promo} \u00b7 Limited time")

    return {
        "id": entry["id"],
        "display": entry["display"],
        "endpoint": entry["endpoint"],
        "sdk": entry["sdk"],
        "price": {
            "input": go_price["input"],
            "output": go_price["output"],
            "cache_read": go_price["cache_read"],
            "cache_write": go_price["cache_write"],
            "monthly_limit": go_price["monthly_limit"],
        },
        "monthly_limit": go_price["monthly_limit"],
        "requests": None
        if go_req is None
        else {
            "five_hour": go_req["five_hour"],
            "week": go_req["week"],
            "month": go_req["month"],
        },
        "training": privacy.get("training"),
        "retention": privacy.get("retention"),
        "free": free,
        "limited_time": limited,
        "promo": promo,
        "region_excluded": key in region_keys,
        "notes": model_notes,
        "plans": {
            "go": _plan_block(go_price, go_req),
            "go_plus": _plan_block(plus_price, plus_req),
        },
    }


def _build_models(
    ctx: dict, notes: list[dict], regions: list[str], skipped: list[str]
) -> list[dict]:
    notes_by_key: dict[str, list[str]] = {}
    for item in notes:
        notes_by_key.setdefault(fold(item["model"]), []).append(item["text"])
    region_keys = {
        key
        for key, texts in notes_by_key.items()
        if any("not available in" in text.lower() for text in texts)
    }

    models: list[dict] = []
    seen: set[str] = set()
    for entry in ctx["catalog"]:
        if entry["id"] in seen:
            continue
        seen.add(entry["id"])
        model = _build_model(entry, ctx, notes_by_key, region_keys)
        if model is None:
            skipped.append(f"catalog row without Go pricing: {entry['id']}")
            continue
        if model["requests"] is None:
            skipped.append(
                f"no Go request row for {entry['id']} (display {entry['display']!r})"
            )
        models.append(model)
    return models


def _report_unmatched(ctx: dict, models: list[dict], skipped: list[str]) -> None:
    known = {fold(model["display"]) for model in models}
    for plan in PLANS:
        for key, rows in ctx["pricing"][plan].items():
            if key in known:
                continue
            for row in rows:
                skipped.append(
                    f"pricing[{plan}] unmatched row: {row['label']} | "
                    f"{row['input']['raw']} | {row['output']['raw']} | "
                    f"{row['monthly_limit']['raw']}"
                )
        for key, row in ctx["requests"][plan].items():
            if key in known:
                continue
            skipped.append(
                f"requests[{plan}] unmatched row: {row['label']} | "
                f"{row['five_hour']['raw']} | {row['week']['raw']} | {row['month']['raw']}"
            )
    for key, row in ctx["privacy"].items():
        if key not in known:
            skipped.append(
                f"privacy unmatched row: {row['label']} | "
                f"{row['training']} | {row['retention']}"
            )


def parse(body: str) -> dict:
    reader = TableReader()
    reader.feed(body)
    skipped: list[str] = []
    ctx = _new_context()

    for table in reader.tables:
        _consume_table(table, ctx, skipped)

    prose_notes, regions = parse_prose(body)
    models = _build_models(ctx, prose_notes, regions, skipped)
    _report_unmatched(ctx, models, skipped)

    for line in skipped:
        print(f"skipped_row: {line}", file=sys.stderr)
    print(f"skipped_rows: {len(skipped)}", file=sys.stderr)

    return {
        "models": models,
        "plans": ctx["plan_info"],
        "regions": regions,
        "skipped_rows": len(skipped),
    }


# --------------------------------------------------------------------------
# output
# --------------------------------------------------------------------------


def _plan_section(key: str, info: dict, models: list[dict]) -> dict:
    return {
        "name": info["name"],
        "price": info["price"],
        "included": info["included"],
        "models": {
            model["id"]: model["plans"][key]
            for model in models
            if model["plans"][key]["listed"]
        },
    }


def _project_model(model: dict, plan: str) -> dict:
    block = model["plans"][plan]
    projected = dict(model)
    projected["price"] = block["price"] or model["price"]
    projected["monthly_limit"] = block["monthly_limit"]
    projected["requests"] = block["requests"]
    return projected


def _project_models(models: list[dict], plan: str | None) -> list[dict]:
    if plan is None:
        return models
    return [
        _project_model(model, plan)
        for model in models
        if model["plans"][plan]["listed"]
    ]


def build_document(parsed: dict, meta: dict, plan_filter: str | None) -> dict:
    models = parsed["models"]
    plans = {
        key: _plan_section(key, parsed["plans"][key], models)
        for key in PLANS
        if not plan_filter or key == plan_filter
    }
    out_models = _project_models(models, plan_filter)
    return {
        "fetched_at": meta.get("fetched_at"),
        "source_url": SOURCE_URL,
        "cache": meta.get("cache"),
        "cache_source": meta.get("source"),
        "plan_filter": plan_filter,
        "plans": plans,
        "free_models": [model["id"] for model in out_models if model["free"]],
        "region_exclusions": parsed["regions"],
        "skipped_rows": parsed["skipped_rows"],
        "models": out_models,
    }


def _table_header(plans: list[str]) -> list[str]:
    return (
        ["id"]
        + [f"{plan.replace('_', '+')} cap" for plan in plans]
        + [f"req/mo {plan.replace('_', '+')}" for plan in plans]
        + ["free", "training"]
    )


def _table_row(model: dict, plans: list[str]) -> list[str]:
    caps, reqs = [], []
    for plan in plans:
        block = model["plans"][plan]
        caps.append(block["monthly_limit"]["raw"] if block["monthly_limit"] else "-")
        reqs.append(block["requests"]["month"]["raw"] if block["requests"] else "-")
    return [
        model["id"],
        *caps,
        *reqs,
        "yes" if model["free"] else "-",
        model["training"] or "-",
    ]


def _grid(header: list[str], rows: list[list[str]]) -> str:
    widths = [len(item) for item in header]
    for row in rows:
        widths = [max(width, len(value)) for width, value in zip(widths, row)]
    lines = [
        "  ".join(value.ljust(widths[index]) for index, value in enumerate(header)),
        "  ".join("-" * width for width in widths),
    ]
    lines.extend(
        "  ".join(value.ljust(widths[index]) for index, value in enumerate(row))
        for row in rows
    )
    return "\n".join(lines)


def render_table(doc: dict, plan_filter: str | None) -> str:
    plans = [plan_filter] if plan_filter else list(PLANS)
    header = _table_header(plans)
    rows = [_table_row(model, plans) for model in doc["models"]]
    return _grid(header, rows)


# --------------------------------------------------------------------------
# cli
# --------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Parse the OpenCode Go model catalog from opencode.ai/docs/go/.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Values keep the raw page string and a parsed number. `--offline` "
        "never touches the network; `--refresh` always does.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--json",
        action="store_const",
        const="json",
        dest="mode",
        help="JSON document (default)",
    )
    mode.add_argument(
        "--table",
        action="store_const",
        const="table",
        dest="mode",
        help="compact plain-text table",
    )
    mode.add_argument(
        "--ids",
        action="store_const",
        const="ids",
        dest="mode",
        help="model ids, one per line, page order",
    )
    mode.add_argument(
        "--ids-for-plan",
        metavar="PLAN",
        choices=list(PLANS),
        help="like --ids, restricted to one plan block",
    )
    parser.add_argument(
        "--plan",
        choices=list(PLANS),
        help="restrict JSON/table output to one plan block",
    )
    parser.add_argument(
        "--cache",
        default=DEFAULT_CACHE,
        help=f"raw HTML cache path (default: {DEFAULT_CACHE})",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="parse the cache; fail loudly when it is missing",
    )
    parser.add_argument("--refresh", action="store_true", help="force a network fetch")
    parser.add_argument(
        "--max-age",
        type=int,
        default=DEFAULT_MAX_AGE,
        help=f"cache freshness in seconds (default {DEFAULT_MAX_AGE})",
    )
    parser.add_argument(
        "--timeout", type=float, default=30.0, help="fetch timeout in seconds"
    )
    parser.add_argument(
        "--diff-models-dev",
        metavar="PROVIDER",
        nargs="?",
        const="opencode-go",
        default=None,
        help="compare the live catalog with models.dev for one provider "
        "(default opencode-go): prints what models.dev still lists that the "
        "live catalog dropped (retired, or never shipped) and the reverse",
    )
    parser.add_argument(
        "--models-dev-cache",
        default=MODELS_DEV_CACHE,
        help=f"models.dev cache path (default: {MODELS_DEV_CACHE})",
    )
    parser.add_argument(
        "--models-dev-max-age",
        type=int,
        default=DEFAULT_MAX_AGE,
        help="models.dev cache freshness in seconds",
    )
    return parser


def load_models_dev_ids(provider, cache_path, max_age, offline):
    """Return the model ids models.dev lists for one provider.

    The cache is shared with lint-preset.py: whoever runs first refreshes it.
    models.dev lags the server (it kept listing `space-bunny` after Go
    retired it), so this set is a candidate list, never a liveness proof.
    """
    import json as _json

    payload = None
    if os.path.exists(cache_path):
        age = time.time() - os.path.getmtime(cache_path)
        if offline or age <= max_age:
            with open(cache_path, encoding="utf-8") as handle:
                payload = handle.read()
        else:
            print(
                "models-dev: cache stale (%.0fs old) — refetching" % age,
                file=sys.stderr,
            )
    if payload is None:
        if offline:
            raise SystemExit(
                "error: --diff-models-dev with --offline needs a cache at %s"
                % cache_path
            )
        request = urllib.request.Request(
            MODELS_DEV_URL, headers={"User-Agent": USER_AGENT}
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read().decode("utf-8")
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        tmp = cache_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as handle:
            handle.write(payload)
        os.replace(tmp, cache_path)
    data = _json.loads(payload)
    block = data.get(provider) or {}
    models = block.get("models") or {}
    return set(models), os.path.getmtime(cache_path)


def print_models_dev_diff(live_ids, provider, cache_path, max_age, offline):
    """Print the two-way diff between the live catalog and models.dev."""
    try:
        dev_ids, mtime = load_models_dev_ids(provider, cache_path, max_age, offline)
    except SystemExit:
        raise
    except Exception as exc:  # network/parse failure must not hide the ids
        print("models-dev: unavailable (%s)" % exc, file=sys.stderr)
        return
    stale = sorted(dev_ids - live_ids)
    fresh = sorted(live_ids - dev_ids)
    print(
        "models-dev: %s (%d ids) vs live catalog (%d ids)"
        % (provider, len(dev_ids), len(live_ids))
    )
    print("in models.dev, not in the live catalog: %s" % (", ".join(stale) or "none"))
    print("in the live catalog, not in models.dev: %s" % (", ".join(fresh) or "none"))
    print("stale_models_dev: %d" % len(stale))


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    body, meta = load_html(args)
    parsed = parse(body)

    plan_filter = args.plan
    mode = args.mode or "json"
    if args.ids_for_plan:
        plan_filter = args.ids_for_plan
        mode = "ids"

    doc = build_document(parsed, meta, plan_filter)

    if args.diff_models_dev:
        live_ids = {model["id"] for model in doc["models"]}
        print_models_dev_diff(
            live_ids,
            args.diff_models_dev,
            args.models_dev_cache,
            args.models_dev_max_age,
            args.offline,
        )
        return 0

    if mode == "ids":
        for model in doc["models"]:
            print(model["id"])
    elif mode == "table":
        print(render_table(doc, plan_filter))
    else:
        json.dump(doc, sys.stdout, indent=2)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
