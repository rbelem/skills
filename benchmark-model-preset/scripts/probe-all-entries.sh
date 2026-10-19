#!/usr/bin/env bash
# Probe EVERY chain entry in a preset (and the root custom agents) for liveness.
#
# Usage: probe-all-entries.sh [preset] [seat-filter] [--probe-retired]
#   probe-all-entries.sh default            # every entry, every seat
#   probe-all-entries.sh default librarian  # only seats/ids matching "librarian"
#   probe-all-entries.sh default "" --probe-retired   # also probe retired ids
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
# Free pre-pass: an opencode-go id that the live Go catalog no longer lists is
# retired, and probing it only burns quota to learn what the catalog already
# says — those entries are reported RETIRED and skipped unless
# --probe-retired is passed.

set -uo pipefail

PRESET="${1:-default}"
FILTER="${2:-}"
PROBE_RETIRED=0
for arg in "$@"; do
    [ "$arg" = "--probe-retired" ] && PROBE_RETIRED=1
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$HOME/.config/opencode/oh-my-opencode-slim.jsonc"

ENTRIES=$(python3 "$SCRIPT_DIR/probe-all-entries.py" "$CONFIG" "$PRESET" --agents)
if [ -z "$ENTRIES" ]; then
    echo "no entries parsed for preset '$PRESET' in $CONFIG" >&2
    exit 2
fi

# Live Go catalog (cached, free): ids the server still serves.
LIVE_IDS=""
if [ "$PROBE_RETIRED" -eq 0 ]; then
    LIVE_IDS=$(python3 "$SCRIPT_DIR/go-catalog.py" --ids 2>/dev/null)
fi

UP=0
DOWN=0
RETIRED=0
while IFS=$'\t' read -r seat head; do
    [ -n "$FILTER" ] && [[ "$seat $head" != *"$FILTER"* ]] && continue
    mid="${head%%#*}"
    provider="${mid%%/*}"
    model="${mid#*/}"
    if [ -n "$LIVE_IDS" ] && [ "$provider" = "opencode-go" ]; then
        if ! printf '%s\n' "$LIVE_IDS" | grep -qx -- "$model"; then
            printf '%-22s %-48s %s\n' "$seat" "$head" "RETIRED (not in the live Go catalog)"
            RETIRED=$((RETIRED + 1))
            continue
        fi
    fi
    out=$("$SCRIPT_DIR/probe-model.sh" "$head" </dev/null 2>&1 | tail -1)
    printf '%-22s %-48s %s\n' "$seat" "$head" "$out"
    case "$out" in
        UP*) UP=$((UP + 1)) ;;
        *) DOWN=$((DOWN + 1)) ;;
    esac
done <<< "$ENTRIES"

echo
echo "Result: $UP up, $DOWN down, $RETIRED retired (skipped without --probe-retired)."
[ "$DOWN" -gt 0 ] && exit 1
exit 0
