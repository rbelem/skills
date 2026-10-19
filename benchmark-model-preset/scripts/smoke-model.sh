#!/usr/bin/env bash
# Smoke test one model: (1) bash tool call, (2) vision QA.
#
# Usage: smoke-model.sh <provider/model[#variant]>
#   ./smoke-model.sh opencode-go/minimax-m3.1-flash-free#low
#
# Why: probe-model.sh proves a model answers, not that it can *use tools* or
# *read images*. The observer seat needs both. A model that reads shapes but
# mangles a character token is not observer-grade (Oct 19: MiniMax M3.1 Flash
# read VQA-7319-M3F as V0A-7319-M3F — Q→0).
#
# Ground truth = the session message record (applied model, tool parts, text).

set -uo pipefail

M="${1:-}"
if [ -z "$M" ]; then
    echo "Usage: smoke-model.sh <provider/model[#variant]>" >&2
    exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRATCH="${SMOKE_DIR:-/tmp/opencode/smoke-dir}"
IMG="${SMOKE_IMG:-/tmp/opencode/vqa-smoke.png}"
mkdir -p "$SCRATCH"

python3 "$SCRIPT_DIR/make-vqa-image.py" "$IMG" >/dev/null

run() {
    local sid raw
    raw=$(cd "$SCRATCH" && timeout 240 opencode run --format json --auto --model "$M" "$@" 2>&1)
    sid=$(printf '%s' "$raw" | python3 -c "
import json, sys
for line in sys.stdin:
    line = line.strip()
    if not line.startswith('{'):
        continue
    try:
        d = json.loads(line)
    except Exception:
        continue
    sid = d.get('sessionID') or (d.get('part') or {}).get('sessionID')
    if sid:
        print(sid)
        break
")
    if [ -z "${sid:-}" ]; then
        echo "  NO SESSION ID"
        printf '%s\n' "$raw" | tail -4
        return 1
    fi
    (cd "$SCRATCH" && opencode api get "/api/session/$sid/message" 2>/dev/null) | python3 "$SCRIPT_DIR/session-report.py"
}

echo "=== TOOL CALL: $M ==="
run 'Use the bash tool to run exactly: echo TOOLCALL-OK-2291 . Then reply with the exact output of that command and nothing else.'
echo
echo "=== VISION: $M ==="
run -f "$IMG" 'Read the image. Reply with exactly three lines: TOKEN: <the text you see>, SHAPES: <the three shapes in order, top to bottom, with color and filled or unfilled>, DONE.'
