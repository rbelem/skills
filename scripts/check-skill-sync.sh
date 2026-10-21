#!/usr/bin/env bash
# check-skill-sync: report drift between the canonical skills and the live trees.
#
# Why this exists: a skill lives in more than one place. The canonical copy is
# this repo (the global AGENTS.md says "edit anywhere; commit in the Workspace
# repo"), but the skills an agent LOADS are the ones under ~/.agents/skills —
# and those point at ~/.autolearn/personas/default/skills, which holds real
# directory copies. Editing the repo copy alone does not change what loads,
# and nothing said so: a session had to edit both trees and copy between them
# by hand.
#
# The check compares, per skill:
#   - the repo copy against the persona copy, byte for byte
#   - a persona skill that has no repo copy (it would be lost to git clean)
#   - an ~/.config/opencode/skills entry that does not link into this repo
#
# It has a ratchet, like the lint in devbox-global: the drift that is already
# there is listed in .skill-sync-baselines.txt and only reported; NEW drift
# fails. Fix a baseline entry by making the two copies agree, then delete the
# line.
#
# Read-only: it changes nothing.
#
# Usage: scripts/check-skill-sync.sh
# Exit 0 = no new drift. Exit 1 = new drift.

set -uo pipefail

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PERSONA_HOME="${PERSONA_HOME:-$HOME/.autolearn/personas/default/skills}"
OPENCODE_SKILLS="${OPENCODE_SKILLS:-$HOME/.config/opencode/skills}"
BASELINE_FILE="$REPO_ROOT/.skill-sync-baselines.txt"

drift=0
baselined=0
checked=0

report() {
    # report <name> <message>
    local name="$1" message="$2"
    if [[ -f "$BASELINE_FILE" ]] && grep -qxF "$name" "$BASELINE_FILE"; then
        printf 'skill-sync: known drift — %s: %s\n' "$name" "$message"
        baselined=$((baselined + 1))
        return
    fi
    printf 'skill-sync: DRIFT %s: %s\n' "$name" "$message" >&2
    drift=$((drift + 1))
}

if [[ ! -d "$PERSONA_HOME" ]]; then
    printf 'skill-sync: no persona home at %s - nothing to compare\n' "$PERSONA_HOME"
    exit 0
fi

# --- the repo copy against the persona copy -------------------------------
for dir in "$REPO_ROOT"/*/; do
    name="$(basename "$dir")"
    [[ -f "$dir/SKILL.md" ]] || continue
    [[ -d "$PERSONA_HOME/$name" ]] || continue
    checked=$((checked + 1))
    differences="$(diff -rq "$dir" "$PERSONA_HOME/$name" 2>&1)"
    if [[ -n "$differences" ]]; then
        report "$name" "the repo copy and the live copy differ"
        printf '%s\n' "$differences" | sed 's/^/    /' >&2
    fi
done

# --- a live skill with no repo copy ---------------------------------------
for dir in "$PERSONA_HOME"/*/; do
    name="$(basename "$dir")"
    [[ -f "$dir/SKILL.md" ]] || continue
    if [[ ! -f "$REPO_ROOT/$name/SKILL.md" ]]; then
        report "$name" "the live copy has no copy in the repo"
    fi
done

# --- an opencode skills entry that does not link into the repo ------------
if [[ -d "$OPENCODE_SKILLS" ]]; then
    for entry in "$OPENCODE_SKILLS"/*/; do
        name="$(basename "$entry")"
        [[ -e "$entry" ]] || continue
        if [[ ! -L "$entry" ]]; then
            report "$name" "~/.config/opencode/skills/$name is a copy, not a link into the repo"
            continue
        fi
        target="$(readlink -f "$entry")"
        case "$target" in
            "$REPO_ROOT"/*) ;;
            *) report "$name" "~/.config/opencode/skills/$name points outside the repo ($target)" ;;
        esac
    done
fi

if [[ $drift -gt 0 ]]; then
    printf 'skill-sync: FAILED — %d new drift(s), %d known, %d skill(s) compared\n' \
        "$drift" "$baselined" "$checked" >&2
    exit 1
fi

printf 'skill-sync: OK (%d skill(s) compared, %d known drift(s))\n' "$checked" "$baselined"
