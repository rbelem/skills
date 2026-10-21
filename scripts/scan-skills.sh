#!/usr/bin/env bash
# Scan skills with NVIDIA SkillSpector and fail on serious findings.
#
# Usage: scripts/scan-skills.sh [skill-dir ...]
#        no args → every top-level directory with a SKILL.md
#
# A skill runs with the agent's full permissions, so prompt injection,
# data exfiltration, supply-chain and rogue-agent patterns are worth a hard
# gate. The threshold is deliberately high: MEDIUM findings are reported,
# HIGH and CRITICAL findings fail the check.
#
# Accepted findings live in .skillspector-baselines/<skill>.yaml — reviewed
# glob rules, each with a reason. A skill with a baseline file is scanned
# against it, so new findings in that skill still surface.
#
# Env:
#   SKILLSPECTOR_BIN       scanner binary (default: skillspector)
#   SKILLSPECTOR_FAIL_ON   severity that fails the check (default: HIGH)
#   SKILLSPECTOR_BASELINE  extra baseline file applied to every scan

set -uo pipefail

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$REPO_ROOT" || exit 1

BIN="${SKILLSPECTOR_BIN:-skillspector}"
THRESHOLD="${SKILLSPECTOR_FAIL_ON:-HIGH}"
EXTRA_BASELINE="${SKILLSPECTOR_BASELINE:-}"
BASELINE_DIR=".skillspector-baselines"

if ! command -v "$BIN" >/dev/null 2>&1; then
  echo "scan-skills: FAIL scanner '$BIN' not on PATH" >&2
  echo "scan-skills: the nix package lives in devbox-global (devbox.d/skillspector);" >&2
  echo "scan-skills: outside the devbox shell use SKILLSPECTOR_BIN=\$HOME/.local/bin/skillspector" >&2
  echo "scan-skills: with env -u PYTHONPATH - the uv install mixes in the profile's python3.14" >&2
  exit 1
fi

skills=()
if [ "$#" -gt 0 ]; then
  skills=("$@")
else
  for d in */; do
    d=${d%/}
    [ -d "$d" ] || continue
    [ -f "$d/SKILL.md" ] && skills+=("$d")
  done
fi

report=$(mktemp -d)
trap 'rm -rf "$report"' EXIT

failed=0
for skill in "${skills[@]}"; do
  out="$report/${skill//\//_}.json"
  args=(scan "./$skill" --no-llm --format json --output "$out")

  baseline=""
  if [ -f "$BASELINE_DIR/$skill.yaml" ]; then
    baseline="$BASELINE_DIR/$skill.yaml"
  elif [ -n "$EXTRA_BASELINE" ] && [ -f "$EXTRA_BASELINE" ]; then
    baseline="$EXTRA_BASELINE"
  fi
  [ -n "$baseline" ] && args+=(--baseline "$baseline")

  # Exit 1 means the scanner found something; the report is still written.
  # Only a missing report is an error.
  # The uv install at ~/.local/bin/skillspector runs under python3.13 while
  # the devbox profile's python3.14 site-packages sit on PYTHONPATH: the
  # child then mixes the two interpreters and dies with
  # "No module named 'pydantic_core._pydantic_core'", producing no report.
  # Strip the two for the child; the nix package does not need them.
  env -u PYTHONPATH -u PYTHONHOME "$BIN" "${args[@]}" >/dev/null 2>&1

  if [ ! -f "$out" ]; then
    echo "scan-skills: FAIL $skill — scanner produced no report" >&2
    failed=1
    continue
  fi

  python3 - "$skill" "$out" "$THRESHOLD" <<'PY'
import json, sys

skill, path, threshold = sys.argv[1], sys.argv[2], sys.argv[3]
order = ["NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
try:
    report = json.load(open(path))
except Exception as exc:
    print(f"scan-skills: FAIL {skill} — unreadable report: {exc}")
    raise SystemExit(1)

risk = report.get("risk_assessment", {}) or {}
max_sev = (risk.get("max_issue_severity") or "NONE").upper()
score = risk.get("score")
issues = report.get("issues") or []
suppressed = report.get("suppressed_count") or 0
failing = order.index(max_sev) >= order.index(threshold)

tag = "FAIL" if failing else "ok  "
print(f"scan-skills: {tag} {skill} — score={score} severity={risk.get('severity')} max_issue={max_sev} issues={len(issues)} suppressed={suppressed}")
for issue in issues:
    ident = issue.get("id") or issue.get("finding_id") or "issue"
    pattern = issue.get("pattern") or issue.get("category") or ""
    where = (issue.get("location") or {}).get("start_line")
    message = str(issue.get("finding") or issue.get("explanation") or "")
    print(f"    - {issue.get('severity')} {ident} {pattern} (line {where}): {message[:140]}")

if failing:
    raise SystemExit(1)
PY
  [ $? -ne 0 ] && failed=1
done

if [ "$failed" -ne 0 ]; then
  echo "scan-skills: FAILED — fix the findings or accept them in $BASELINE_DIR" >&2
  exit 1
fi

echo "scan-skills: OK (${#skills[@]} skill(s) scanned, threshold=$THRESHOLD)"
exit 0
