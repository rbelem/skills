#!/usr/bin/env python3
"""Print chain heads (seat <TAB> id[#variant]) for a preset.

Reads oh-my-opencode-slim.jsonc: presets.<name> agents plus
council.presets.<name> seats. Handles per-entry {id, variant} objects,
bare id strings, and councillor plain-string lists (seat-level variant).

Usage: probe-heads.py <config.jsonc> <preset>
"""

import json
import sys


def strip_jsonc(text):
    """Remove // and /* */ comments, respecting double-quoted strings."""
    out = []
    i, n = 0, len(text)
    in_str = False
    esc = False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
        elif c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
        elif c == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def head_of(model, seat_variant):
    """Return id[#variant] for the first entry of a model list."""
    if not model:
        return None
    first = model[0] if isinstance(model, list) else model
    if isinstance(first, dict):
        v = first.get("variant") or seat_variant
        return first["id"] + ("#" + v if v else "")
    v = seat_variant
    return first + ("#" + v if v else "")


def main():
    config_path, preset = sys.argv[1], sys.argv[2]
    with open(config_path) as f:
        cfg = json.loads(strip_jsonc(f.read()))

    presets = cfg.get("presets", {})
    if preset not in presets:
        print(f"preset '{preset}' not found", file=sys.stderr)
        sys.exit(2)

    for seat, entry in presets[preset].items():
        if not isinstance(entry, dict) or "model" not in entry:
            continue
        head = head_of(entry["model"], entry.get("variant"))
        if head:
            print(f"{seat}\t{head}")

    council = ((cfg.get("council") or {}).get("presets") or {}).get(preset, {})
    for seat, entry in council.items():
        if not isinstance(entry, dict) or "model" not in entry:
            continue
        head = head_of(entry["model"], entry.get("variant"))
        if head:
            print(f"council.{seat}\t{head}")


if __name__ == "__main__":
    main()
