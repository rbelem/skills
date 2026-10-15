#!/bin/bash
# OpenCode Go endpoint liveness check — current model list (Oct 15, 2026).
#
# Usage: ./scripts/test-endpoints.sh [API_KEY]
# Key resolution order: $1 → $OPENCODE_GO_API_KEY → opencode auth.json
# (provider "opencode-go").
#
# Go serves three access modes (discovered 2026-10-15):
#   1. OpenAI-compatible  POST /chat/completions  (all open-weight models)
#   2. Anthropic-compatible POST /messages        (claude-haiku-5-5, minimax-m2.7)
#   3. client-only protocol                        (grok/gpt/gemini/muse — raw curl
#      returns 400 ModelProtocolUnsupported; verify with
#      `opencode run --model opencode-go/<id> 'Reply with exactly: OK'`)
#
# Raw curl requirements: non-SDK User-Agent (Cloudflare bans generic signatures
# with 403 code 1010) + x-opencode-session (Go routes agents by it).
# Free previews (longcat-2.5-preview-free, step-5-preview-free, cat-jam-free)
# are unlimited but "limited time" — re-check them each refresh.

set -uo pipefail

BASE_URL="${OPENCODE_GO_BASE_URL:-https://opencode.ai/inference/go/v1}"

if [ -n "${1:-}" ]; then
    API_KEY="$1"
elif [ -n "${OPENCODE_GO_API_KEY:-}" ]; then
    API_KEY="$OPENCODE_GO_API_KEY"
else
    API_KEY=$(python3 - <<'PY' 2>/dev/null
import json, os
p = os.path.expanduser("~/.local/share/opencode/auth.json")
try:
    print(json.load(open(p))["opencode-go"]["key"])
except Exception:
    pass
PY
)
fi

if [ -z "${API_KEY:-}" ]; then
    echo "Error: no API key (arg, \$OPENCODE_GO_API_KEY, or auth.json opencode-go)."
    exit 1
fi

# OpenAI-compatible /chat/completions
declare -a OPENAI_MODELS=(
    "cat-jam-free"
    "deepseek-v4-pro"
    "deepseek-v4.1-flash"
    "glm-5.2"
    "glm-5.3"
    "glm-5.3-flash"
    "hy3"
    "hy4-preview"
    "kimi-k2.7-code"
    "kimi-k3"
    "longcat-2.0"
    "longcat-2.5-preview-free"
    "mimo-v2.5"
    "mimo-v2.5-pro"
    "mimo-v2.6-flash"
    "mimo-v2.6-pro"
    "minimax-m3"
    "qwen3.7-plus"
    "qwen3.8-flash"
    "qwen3.8-max"
    "space-bunny"
    "step-5-preview-free"
)

# Anthropic-compatible /messages
declare -a ANTHROPIC_MODELS=(
    "claude-haiku-5-5"
    "minimax-m2.7"
)

# Client-only protocol: raw HTTP not supported. Verify via `opencode run`.
declare -a CLIENT_ONLY_MODELS=(
    "gemini-4-argon-contributor"
    "gpt-5.6-luna"
    "gpt-6-luna"
    "grok-4.6"
    "grok-4.7"
    "muse-spark-1.2-contributor"
    "muse-spark-1.3-contributor"
)

TEST_PROMPT="Reply with exactly: OK"
MAX_TOKENS=512
CONNECT_TIMEOUT=10
MAX_TIME=90

echo "=============================================="
echo "OpenCode Go Endpoint Health Check ($(date -u +%FT%TZ))"
echo "Base URL: $BASE_URL"
echo "Models: $(( ${#OPENAI_MODELS[@]} + ${#ANTHROPIC_MODELS[@]} + ${#CLIENT_ONLY_MODELS[@]} ))"
echo "=============================================="

TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

run_probe() {
    # run_probe <protocol> <model> ; protocol: openai|anthropic
    local proto=$1 model=$2
    local outfile="$TMPDIR/${model}.txt"
    local response http_code time_total

    if [ "$proto" = "openai" ]; then
        response=$(curl -s -w '\n%{http_code} %{time_total}' -X POST \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $API_KEY" \
            -H "User-Agent: opencode-go-healthcheck/1.0" \
            -H "x-opencode-session: healthcheck-${model}" \
            -d "{\"model\":\"$model\",\"messages\":[{\"role\":\"user\",\"content\":\"$TEST_PROMPT\"}],\"max_tokens\":$MAX_TOKENS}" \
            "${BASE_URL}/chat/completions" \
            --connect-timeout $CONNECT_TIMEOUT --max-time $MAX_TIME 2>/dev/null \
            || echo '{"error":{"message":"Connection failed"}}')
    else
        response=$(curl -s -w '\n%{http_code} %{time_total}' -X POST \
            -H "Content-Type: application/json" \
            -H "x-api-key: $API_KEY" \
            -H "anthropic-version: 2023-06-01" \
            -H "User-Agent: opencode-go-healthcheck/1.0" \
            -H "x-opencode-session: healthcheck-${model}" \
            -d "{\"model\":\"$model\",\"max_tokens\":$MAX_TOKENS,\"messages\":[{\"role\":\"user\",\"content\":\"$TEST_PROMPT\"}]}" \
            "${BASE_URL}/messages" \
            --connect-timeout $CONNECT_TIMEOUT --max-time $MAX_TIME 2>/dev/null \
            || echo '{"error":{"message":"Connection failed"}}')
    fi

    local meta body
    meta=$(printf '%s' "$response" | tail -1)
    http_code=$(printf '%s' "$meta" | awk '{print $1}')
    time_total=$(printf '%s' "$meta" | awk '{print $2}')
    body=$(printf '%s' "$response" | sed '$d')

    if [[ "$http_code" == "200" ]] && { printf '%s' "$body" | grep -q '"choices"'; printf '%s' "$body" | grep -q '"content"'; }; then
        echo "✅ UP (${time_total}s)" > "$outfile"
    elif printf '%s' "$body" | grep -q '"error"'; then
        local error_msg
        error_msg=$(printf '%s' "$body" | grep -oP '"message":\s*"[^"]*"' | head -1 | cut -d'"' -f4 || echo "unknown error")
        echo "❌ DOWN [${http_code:-?}]: $error_msg" > "$outfile"
    else
        echo "❌ DOWN [${http_code:-?}]: no valid response" > "$outfile"
    fi
}

for model in "${OPENAI_MODELS[@]}"; do
    run_probe openai "$model" &
done
for model in "${ANTHROPIC_MODELS[@]}"; do
    run_probe anthropic "$model" &
done
wait

UP=0
DOWN=0
for model in "${OPENAI_MODELS[@]}" "${ANTHROPIC_MODELS[@]}"; do
    result=$(cat "$TMPDIR/${model}.txt" 2>/dev/null || echo "? No result")
    printf '%-32s %s\n' "$model" "$result"
    if [[ "$result" == *"✅ UP"* ]]; then ((UP++)); else ((DOWN++)); fi
done
for model in "${CLIENT_ONLY_MODELS[@]}"; do
    printf '%-32s ➖ SKIP (client-only protocol; verify via opencode run)\n' "$model"
done

echo ""
echo "=============================================="
echo "Results: $UP up, $DOWN down (raw-HTTP subset; ${#CLIENT_ONLY_MODELS[@]} client-only skipped)"
echo "=============================================="

[ $DOWN -gt 0 ] && exit 1
exit 0
