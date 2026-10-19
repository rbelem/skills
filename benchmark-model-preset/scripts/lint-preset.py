#!/usr/bin/env python3
"""Lint the oh-my-opencode-slim preset chains against models.dev, offline-first.

Catches the deterministic classes that `oh-my-opencode-slim doctor` passes:
BAD-VARIANT (variant not usable by that model), UNKNOWN-MODEL (provider or id
absent from models.dev), BARE-ENTRY (bare string inside a seat that declares a
seat-level variant), SEAT-VARIANT-MISMATCH (seat variant differs from chain[0],
and the seat variant is what the head actually runs at), and EMPTY-CHAIN.

models.dev is cached at scripts/out/models-dev.json and re-fetched only when
older than --max-age-hours (default 24). No API key, no quota, no live probe:
a models.dev hit means "candidate", not "serving".

BARE-ENTRY is exempt inside council seats, whose documented shape is plain
strings plus a seat-level variant; their inherited variant is still checked
for BAD-VARIANT.

Usage: lint-preset.py [--config PATH] [--preset NAME] [--offline] [--json]
"""

import argparse
import importlib.util as _ilu
import json
import os
import sys
import time
import urllib.request

MODELS_DEV_URL = "https://models.dev/api.json"
DEFAULT_CONFIG = "~/.config/opencode/oh-my-opencode-slim.jsonc"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CACHE = os.path.join(SCRIPT_DIR, "out", "models-dev.json")

# Only these variant strings are usable on a model without an effort option.
NO_EFFORT_VARIANTS = (None, "default")


def load_strip_jsonc():
    """Import strip_jsonc from probe-heads.py (hyphenated name, not importable)."""
    spec = _ilu.spec_from_file_location(
        "probe_heads", os.path.join(SCRIPT_DIR, "probe-heads.py")
    )
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.strip_jsonc


strip_jsonc = load_strip_jsonc()


def cache_age_hours(path):
    """Return cache age in hours, or None when the file does not exist."""
    try:
        return (time.time() - os.path.getmtime(path)) / 3600.0
    except OSError:
        return None


def read_cache(path):
    """Load the cached models.dev document."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as exc:
        sys.exit("error: cache %s unreadable (%s); delete it and rerun" % (path, exc))


def download(cache_path):
    """Fetch models.dev and replace the cache atomically; raise on failure."""
    req = urllib.request.Request(
        MODELS_DEV_URL, headers={"User-Agent": "lint-preset/1.0"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
    doc = json.loads(raw.decode("utf-8"))
    os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
    tmp = cache_path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(raw)
    os.replace(tmp, cache_path)
    return doc


def get_data(cache_path, max_age_hours, offline):
    """Return (document, info); re-fetch only when the cache is stale."""
    age = cache_age_hours(cache_path)
    if offline:
        if age is None:
            sys.exit(
                "error: --offline given but no cache at %s "
                "(run once without --offline)" % cache_path
            )
        return read_cache(cache_path), {
            "path": cache_path,
            "age": age,
            "fetched": False,
        }
    if age is not None and age < max_age_hours:
        return read_cache(cache_path), {
            "path": cache_path,
            "age": age,
            "fetched": False,
        }
    try:
        doc = download(cache_path)
    except Exception as exc:  # network, HTTP, or bad JSON
        if age is None:
            sys.exit(
                "error: cannot fetch %s and no cache at %s: %s"
                % (MODELS_DEV_URL, cache_path, exc)
            )
        print("warning: fetch failed (%s); using stale cache" % exc, file=sys.stderr)
        return read_cache(cache_path), {
            "path": cache_path,
            "age": age,
            "fetched": False,
        }
    return doc, {"path": cache_path, "age": 0.0, "fetched": True}


def providers_of(doc):
    """models.dev serves providers at top level; accept a {"providers"} wrapper too."""
    if isinstance(doc, dict) and isinstance(doc.get("providers"), dict):
        return doc["providers"]
    return doc if isinstance(doc, dict) else {}


def effort_values(model):
    """Return the model's effort-value list, or None when it has no effort option."""
    options = model.get("reasoning_options") or []
    if not isinstance(options, list):
        return None
    for opt in options:
        if isinstance(opt, dict) and opt.get("type") == "effort":
            values = opt.get("values") or []
            if isinstance(values, list):
                return list(values)
    return None


def split_entry(raw):
    """Return (id, written_variant, is_bare_string) for one chain entry."""
    if isinstance(raw, dict):
        return raw.get("id"), raw.get("variant"), False
    if isinstance(raw, str):
        return raw, None, True
    return None, None, False


def variant_problem(effective, values):
    """Return an error message for an unusable variant, or None when it is fine."""
    if values is None:
        if effective in NO_EFFORT_VARIANTS:
            return None
        return (
            "model has no effort option; only absent or 'default' is accepted "
            "(got '%s')" % effective
        )
    if effective is None or effective in values:
        return None
    return "variant '%s' not in model effort values [%s]" % (
        effective,
        ", ".join(str(v) for v in values),
    )


def lookup_model(mid, providers, seat, shown, add):
    """Return models.dev model info, or None after reporting UNKNOWN-MODEL."""
    provider, _, model_id = mid.partition("/")
    if not model_id:
        add(
            "error",
            seat,
            shown,
            "UNKNOWN-MODEL",
            "id has no 'provider/model' separator",
        )
        return None
    block = providers.get(provider)
    if not isinstance(block, dict):
        add(
            "error",
            seat,
            shown,
            "UNKNOWN-MODEL",
            "provider '%s' not in models.dev" % provider,
        )
        return None
    models = block.get("models")
    info = models.get(model_id) if isinstance(models, dict) else None
    if not isinstance(info, dict):
        add(
            "error",
            seat,
            shown,
            "UNKNOWN-MODEL",
            "model not listed under provider '%s' in models.dev" % provider,
        )
        return None
    return info


def check_entry(seat, raw, seat_variant, providers, add, warn_bare=True):
    """Check one chain entry; return {id, written, effective}."""
    mid, written, bare = split_entry(raw)
    if not isinstance(mid, str) or not mid:
        add(
            "error",
            seat,
            "-",
            "EMPTY-CHAIN",
            "entry is not a model id (got %r)" % (raw,),
        )
        return {"id": None, "written": None, "effective": None}

    effective = written
    if bare and seat_variant:
        effective = seat_variant
        if warn_bare:
            add(
                "warning",
                seat,
                mid + "#" + str(seat_variant),
                "BARE-ENTRY",
                "bare string inherits seat variant '%s'; write {id, variant} "
                "explicitly" % seat_variant,
            )

    shown = mid + ("#" + str(effective) if effective else "")
    info = lookup_model(mid, providers, seat, shown, add)
    if info is not None:
        problem = variant_problem(effective, effort_values(info))
        if problem:
            add("error", seat, shown, "BAD-VARIANT", problem)
    return {"id": mid, "written": written, "effective": effective}


def head_label(first, seat_variant):
    """Resolved head: the seat variant wins at runtime when it is declared."""
    if not first or not first["id"]:
        return None
    variant = seat_variant or first["written"]
    return first["id"] + ("#" + str(variant) if variant else "")


def lint_seat(seat, entry, providers, add):
    """Check one seat and return its inventory row."""
    model = entry.get("model")
    seat_variant = entry.get("variant")
    row = {"seat": seat, "head": None, "entries": 0, "variant": seat_variant}

    if not isinstance(model, (list, str)):
        add(
            "error",
            seat,
            "-",
            "EMPTY-CHAIN",
            "model is %s, expected a list or a string" % type(model).__name__,
        )
        return row
    chain = [model] if isinstance(model, str) else model
    if not chain:
        add("error", seat, "-", "EMPTY-CHAIN", "model list is empty")
        return row

    row["entries"] = len(chain)
    first = None
    # Council seats carry the variant at seat level by design: a plain string is
    # the documented shape there, so only flag inheritance elsewhere.
    warn_bare = not seat.startswith("council.")
    for index, raw in enumerate(chain):
        result = check_entry(seat, raw, seat_variant, providers, add, warn_bare)
        if index == 0:
            first = result
    row["head"] = head_label(first, seat_variant)

    if seat_variant and first["written"] and seat_variant != first["written"]:
        add(
            "warning",
            seat,
            row["head"],
            "SEAT-VARIANT-MISMATCH",
            "seat variant '%s' overrides chain[0] variant '%s'; the head runs "
            "at '%s'" % (seat_variant, first["written"], seat_variant),
        )
    return row


def presets_block(cfg):
    """Return the presets mapping or exit when the config has none."""
    presets = cfg.get("presets")
    if not isinstance(presets, dict):
        sys.exit("error: 'presets' is not an object")
    return presets


def seat_items(block):
    """Return (name, entry) pairs that declare a model key."""
    if not isinstance(block, dict):
        return []
    return [
        (name, entry)
        for name, entry in block.items()
        if isinstance(entry, dict) and "model" in entry
    ]


def collect_seats(cfg, preset):
    """Return [(label, entry)] for preset seats, council seats, and root agents."""
    presets = presets_block(cfg)
    if preset not in presets:
        sys.exit(
            "error: preset '%s' not found (known: %s)"
            % (preset, ", ".join(sorted(presets)) or "(none)")
        )
    council = ((cfg.get("council") or {}).get("presets") or {}).get(preset) or {}
    seats = seat_items(presets.get(preset))
    seats += [("council." + name, entry) for name, entry in seat_items(council)]
    seats += [("agent." + name, entry) for name, entry in seat_items(cfg.get("agents"))]
    return seats


def lint(config_path, preset, providers):
    """Return (findings, seat_rows) for one preset."""
    with open(config_path, encoding="utf-8") as f:
        cfg = json.loads(strip_jsonc(f.read()))

    findings = []
    rows = []

    def add(severity, seat, idv, rule, message):
        findings.append(
            {
                "severity": severity,
                "seat": seat,
                "id": idv,
                "rule": rule,
                "message": message,
            }
        )

    for seat, entry in collect_seats(cfg, preset):
        rows.append(lint_seat(seat, entry, providers, add))

    findings.sort(key=lambda f: (0 if f["severity"] == "error" else 1, f["seat"]))
    return findings, rows


def build_parser():
    parser = argparse.ArgumentParser(
        description="Lint preset model chains against cached models.dev data."
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG,
        help="JSONC config path (default: %(default)s)",
    )
    parser.add_argument(
        "--preset",
        default=None,
        help="preset name (default: config 'preset' field, else 'default')",
    )
    parser.add_argument(
        "--cache",
        default=DEFAULT_CACHE,
        help="models.dev cache path (default: scripts/out/models-dev.json)",
    )
    parser.add_argument(
        "--max-age-hours",
        type=float,
        default=24.0,
        help="re-fetch cache older than this (default: %(default)s)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="use the cache only; fail if it is missing",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    return parser


def emit_text(info, config_path, preset, rows, findings, counts):
    """Print the inventory, the findings, and the summary."""
    state = "fetched" if info["fetched"] else "cache"
    print("data    %s  age=%.1fh  (%s)" % (info["path"], info["age"], state))
    print("config  %s  preset=%s" % (config_path, preset))
    for row in rows:
        print(
            "SEAT    %-22s %-46s entries=%d"
            % (row["seat"], row["head"] or "(no head)", row["entries"])
        )
    if findings:
        print()
    for f in findings:
        print(
            "%-7s %-22s %-46s %s"
            % (f["severity"].upper(), f["seat"], f["id"], f["message"])
        )
    print()
    print(
        "%d error(s), %d warning(s), %d seat(s) checked"
        % (counts["error"], counts["warning"], counts["seats"])
    )


def resolve_preset(config_path, preset):
    """Return the explicit preset, else the config's own, else 'default'."""
    if preset:
        return preset
    with open(config_path, encoding="utf-8") as f:
        return json.loads(strip_jsonc(f.read())).get("preset") or "default"


def run(args):
    """Lint and emit; return the process exit code."""
    config_path = os.path.expanduser(args.config)
    cache_path = os.path.expanduser(args.cache)
    if not os.path.exists(config_path):
        sys.exit("error: config not found: %s" % config_path)

    doc, info = get_data(cache_path, args.max_age_hours, args.offline)
    preset = resolve_preset(config_path, args.preset)
    findings, rows = lint(config_path, preset, providers_of(doc))
    errors = sum(1 for f in findings if f["severity"] == "error")
    counts = {
        "error": errors,
        "warning": sum(1 for f in findings if f["severity"] == "warning"),
        "seats": len(rows),
        "findings": len(findings),
    }

    if args.json:
        print(
            json.dumps(
                {"findings": findings, "seats": rows, "counts": counts}, indent=2
            )
        )
    else:
        emit_text(info, config_path, preset, rows, findings, counts)
    return 1 if errors else 0


def main():
    args = build_parser().parse_args()
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
