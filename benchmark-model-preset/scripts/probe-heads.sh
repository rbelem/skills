#!/usr/bin/env bash
# Probe every chain head in a preset and fail loudly on any dead one.
#
# Usage: probe-heads.sh [preset] [seat...]   (default preset: default)
#
# With seat args, only those seats are probed — refreshes usually touch one
# or two chains, and a full run burns ~$0.40 of paid quota (oracle/designer/
# kimi-k3/council heads all sit on $15 caps). Full runs are for structural
# edits; filtered runs are the daily habit.
# Example: probe-heads.sh budget librarian fast-generic
#
# Why this exists: `bunx oh-my-opencode-slim doctor --json` validates config
# shape and static resolution only — it passes with server-side-retired models
# still in chains (cat-jam-free, step-5-preview-free, Oct 2026: two lanes
# dispatched onto dead primaries before anyone noticed). Run this before
# dispatching lanes or after any preset edit; exit 1 names the dead heads.
#
# Heads are read from the live oh-my-opencode-slim.jsonc (source of truth),
# covering preset agents AND council.presets seats. Each probe is one tiny
# inference call via probe-model.sh.

set -uo pipefail

PRESET="${1:-default}"
if [ "$#" -gt 0 ]; then shift; fi
# Any remaining args are a seat filter (e.g. `librarian fast-generic`,
# `council.alpha`). Empty = all seats.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$HOME/.config/opencode/oh-my-opencode-slim.jsonc"

HEADS=$("$SCRIPT_DIR/probe-heads.py" "$CONFIG" "$PRESET") || exit 2
if [ -z "$HEADS" ]; then
    echo "No chain heads found for preset '$PRESET' in $CONFIG" >&2
    exit 2
fi

echo "Chain heads for preset '$PRESET' ($(printf '%s\n' "$HEADS" | grep -c .) seats):"
if [ "$#" -gt 0 ]; then
    echo "(filter: $*)"
fi
echo "$HEADS"
echo ""

UP=0
DOWN=0
MATCHED=0
TOTAL=0
FAILED=""
while IFS=$'\t' read -r seat head; do
    if [ "$#" -gt 0 ]; then
        want=0
        for f in "$@"; do
            [ "$seat" = "$f" ] && want=1
        done
        [ "$want" = 0 ] && continue
    fi
    MATCHED=$((MATCHED + 1))
    # </dev/null: `opencode run` inherits stdin and would swallow the seat
    # list feeding this loop (Oct-16: a run reported "1 up" for 13 seats).
    if out=$("$SCRIPT_DIR/probe-model.sh" "$head" </dev/null 2>&1); then
        echo "  ✅ $seat <- $out"
        UP=$((UP + 1))
    else
        echo "  ❌ $seat <- $out"
        DOWN=$((DOWN + 1))
        FAILED="$FAILED $seat($head)"
    fi
    c=$(printf '%s' "$out" | grep -oP 'cost=\K[0-9.eE+-]+' | head -1 || true)
    if printf '%s' "$c" | grep -qE '^[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?$'; then
        TOTAL=$(awk -v t="$TOTAL" -v c="$c" 'BEGIN{printf "%.6f", t+c}')
    fi
done <<< "$HEADS"

echo ""
if [ "$#" -gt 0 ] && [ "$MATCHED" -eq 0 ]; then
    echo "No seats matched filter: $*" >&2
    exit 2
fi
echo "Result: $UP up, $DOWN down. Probe spend: \$$TOTAL."
if [ "$DOWN" -gt 0 ]; then
    echo "Dead heads:$FAILED" >&2
    exit 1
fi
exit 0
