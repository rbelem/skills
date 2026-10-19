#!/usr/bin/env bash
# Probe EVERY chain entry in a preset (and the root custom agents) for liveness.
#
# Usage: probe-all-entries.sh [preset] [seat-filter]
#   probe-all-entries.sh default            # every entry, every seat
#   probe-all-entries.sh default librarian  # only seats/ids matching "librarian"
#
# Why this exists next to probe-heads.sh: head-only probing reports a chain
# as healthy while its tail is dead. The Oct 19, 2026 sweep found eight broken
# entries that way (retired `space-bunny` mid-chain, `kimi-k3#high` and
# `qwen3.8-max#high` invalid variants, four bare-string `mimo-v2.6-*` entries
# inheriting an unusable seat variant). Each probe is one tiny inference call
# through probe-model.sh (message API = applied model + cost).
#
# Cost: a full run is ~35 calls, most of them free tiers; the paid seats
# (oracle/designer/council) dominate. Filter when you only need one seat.

set -uo pipefail

PRESET="${1:-default}"
FILTER="${2:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$HOME/.config/opencode/oh-my-opencode-slim.jsonc"

ENTRIES=$(python3 "$SCRIPT_DIR/probe-all-entries.py" "$CONFIG" "$PRESET" --agents)
if [ -z "$ENTRIES" ]; then
    echo "no entries parsed for preset '$PRESET' in $CONFIG" >&2
    exit 2
fi

UP=0
DOWN=0
while IFS=$'\t' read -r seat head; do
    [ -n "$FILTER" ] && [[ "$seat $head" != *"$FILTER"* ]] && continue
    out=$("$SCRIPT_DIR/probe-model.sh" "$head" </dev/null 2>&1 | tail -1)
    printf '%-22s %-48s %s\n' "$seat" "$head" "$out"
    case "$out" in
        UP*) UP=$((UP + 1)) ;;
        *) DOWN=$((DOWN + 1)) ;;
    esac
done <<< "$ENTRIES"

echo
echo "Result: $UP up, $DOWN down."
[ "$DOWN" -gt 0 ] && exit 1
exit 0
