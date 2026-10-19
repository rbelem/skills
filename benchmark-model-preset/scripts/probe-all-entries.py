#!/usr/bin/env python3
"""Print every chain entry (not just heads) for a preset, plus root agents.

Usage: probe-all-entries.py <config.jsonc> <preset> [--agents]

Prints "<seat>\t<id[#variant]>" per line. Head-only probing misses dead
mid-chain fallbacks — the Oct 19, 2026 sweep found eight broken entries
(retired model, invalid variants, bare-string entries inheriting an
unusable seat variant) that every head probe reported as healthy.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# probe-heads.py has a hyphen, so it is not importable by name.
import importlib.util as _ilu

_spec = _ilu.spec_from_file_location(
    "probe_heads",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe-heads.py"),
)
probe_heads = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(probe_heads)
strip_jsonc = probe_heads.strip_jsonc


def entries(model, seat_variant):
    """Flatten a seat's model list into (id, variant) pairs."""
    if not model:
        return []
    if not isinstance(model, list):
        model = [model]
    out = []
    for e in model:
        if isinstance(e, dict):
            out.append((e["id"], e.get("variant") or seat_variant))
        else:
            out.append((e, seat_variant))
    return out


def main():
    config_path, preset = sys.argv[1], sys.argv[2]
    want_agents = "--agents" in sys.argv[3:]
    cfg = json.loads(strip_jsonc(open(config_path).read()))

    rows = []
    for seat, entry in ((cfg.get("presets") or {}).get(preset) or {}).items():
        if isinstance(entry, dict) and "model" in entry:
            rows += [
                (seat, i, v) for i, v in entries(entry["model"], entry.get("variant"))
            ]

    council = ((cfg.get("council") or {}).get("presets") or {}).get(preset) or {}
    for seat, entry in council.items():
        if isinstance(entry, dict) and "model" in entry:
            rows += [
                ("council." + seat, i, v)
                for i, v in entries(entry["model"], entry.get("variant"))
            ]

    if want_agents:
        for seat, entry in (cfg.get("agents") or {}).items():
            if isinstance(entry, dict) and "model" in entry:
                rows += [
                    ("agent." + seat, i, v)
                    for i, v in entries(entry["model"], entry.get("variant"))
                ]

    for seat, mid, var in rows:
        print(f"{seat}\t{mid}" + (f"#{var}" if var else ""))


if __name__ == "__main__":
    main()
