#!/usr/bin/env bash
# Probe one model id through the real stack and report what actually served.
#
# Usage: probe-model.sh <provider/model[#variant]>
# Example: probe-model.sh opencode/glm-5.3-flash-free#low
#
# Why this exists: `opencode run` exits 0 and prints a bare error when a model
# is unavailable, and free-tier misses silently fail over to another model via
# the retry hook. The serving header is also unreliable (missing on some
# providers). So this script resolves the session's message record and reports
# the *applied* provider/model/variant plus cost — the only ground truth.
#
# Output: one VERDICT line. Exit 0 = served by the requested model id,
# exit 1 = failover, unavailable, or any other failure.
#
# Free-tier note: `opencode/*-free` ids need a signed-in OpenCode Console;
# when it lapses they fail over instead of erroring. A FAILOVER verdict on a
# free id usually means "reconnect the Console from the TUI", not "model dead".

set -uo pipefail

if [ -z "${1:-}" ]; then
    echo "Usage: probe-model.sh <provider/model[#variant]>" >&2
    exit 2
fi

WANT="$1"
WANT_ID="${WANT%%#*}"
SCRATCH="${PROBE_DIR:-/tmp/opencode/probe-dir}"
mkdir -p "$SCRATCH"

RAW=$(cd "$SCRATCH" && timeout 120 opencode run --format json --model "$WANT" \
    'reply with the single word ok' 2>&1)

if printf '%s' "$RAW" | grep -q 'Model unavailable'; then
    echo "DOWN  $WANT  (model unavailable on the wire)"
    exit 1
fi

SID=$(printf '%s' "$RAW" | python3 -c "
import json,sys
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
" 2>/dev/null)

if [ -z "${SID:-}" ]; then
    echo "DOWN  $WANT  (no session id in run output)"
    printf '%s\n' "$RAW" | tail -5 >&2
    exit 1
fi

INFO=$(cd "$SCRATCH" && opencode api get "/api/session/$SID/message" 2>/dev/null \
    | python3 -c "
import json,sys
d = json.load(sys.stdin)
msgs = d.get('data', d)
if isinstance(msgs, dict):
    msgs = msgs.get('messages', [])
for m in msgs:
    if m.get('type') == 'assistant' and isinstance(m.get('model'), dict):
        md = m['model']
        print(md.get('providerID'), md.get('id'), md.get('variant'), m.get('cost', '?'))
        break
" 2>/dev/null)

if [ -z "${INFO:-}" ]; then
    echo "DOWN  $WANT  (session $SID has no assistant model record)"
    exit 1
fi

read -r GOT_PROV GOT_ID GOT_VAR GOT_COST <<< "$INFO"
if [ "$GOT_PROV/$GOT_ID" = "$WANT_ID" ] || [ "$GOT_ID" = "$WANT_ID" ]; then
    echo "UP  $WANT  served=$GOT_PROV/$GOT_ID variant=$GOT_VAR cost=$GOT_COST (session $SID)"
    exit 0
fi

echo "FAILOVER  $WANT  served=$GOT_PROV/$GOT_ID variant=$GOT_VAR cost=$GOT_COST (session $SID)"
exit 1
