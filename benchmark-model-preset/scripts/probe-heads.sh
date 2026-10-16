#!/usr/bin/env bash
# Probe every chain head in a preset and fail loudly on any dead one.
#
# Usage: probe-heads.sh [preset]   (default: budget)
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

PRESET="${1:-budget}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$HOME/.config/opencode/oh-my-opencode-slim.jsonc"

HEADS=$("$SCRIPT_DIR/probe-heads.py" "$CONFIG" "$PRESET") || exit 2
if [ -z "$HEADS" ]; then
    echo "No chain heads found for preset '$PRESET' in $CONFIG" >&2
    exit 2
fi

echo "Chain heads for preset '$PRESET' ($(printf '%s\n' "$HEADS" | grep -c .) seats):"
echo "$HEADS"
echo ""

UP=0
DOWN=0
FAILED=""
while IFS=$'\t' read -r seat head; do
    if out=$("$SCRIPT_DIR/probe-model.sh" "$head" </dev/null 2>&1); then
        echo "  ✅ $seat <- $out"
        UP=$((UP + 1))
    else
        echo "  ❌ $seat <- $out"
        DOWN=$((DOWN + 1))
        FAILED="$FAILED $seat($head)"
    fi
done <<< "$HEADS"

echo ""
echo "Result: $UP up, $DOWN down."
if [ "$DOWN" -gt 0 ]; then
    echo "Dead heads:$FAILED" >&2
    exit 1
fi
exit 0
