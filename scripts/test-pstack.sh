#!/usr/bin/env bash
# test-pstack: run the pstack fork's TypeScript test suites.
#
# Two trees, two runners:
#   pstack/skills/statechart/scripts   node --test  (needs fast-check)
#   pstack/skills/poteto-mode/scripts  bun test     (needs commander) + tsc
#
# The statechart TLC tests skip themselves unless TLA2TOOLS points at
# tla2tools.jar. With nix available this script realises nixpkgs#tlaplus and
# uses its jar, so a plain run exercises all 334 tests.
#
# Usage: scripts/test-pstack.sh [--no-tlc]
# Exit 0 = every suite passed.

set -uo pipefail

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SKILLS="$REPO_ROOT/pstack/skills"
STATECHART="$SKILLS/statechart/scripts"
POTETO_MODE="$SKILLS/poteto-mode/scripts"
status=0

if [[ "${1:-}" != "--no-tlc" && -z "${TLA2TOOLS:-}" ]] && command -v nix >/dev/null 2>&1; then
    TLA2TOOLS="$(nix build --no-link --print-out-paths nixpkgs#tlaplus 2>/dev/null)/share/java/tla2tools.jar"
fi
if [[ -n "${TLA2TOOLS:-}" && ! -f "$TLA2TOOLS" ]]; then
    echo "test-pstack: TLA2TOOLS=$TLA2TOOLS is not a file — TLC tests will skip" >&2
    TLA2TOOLS=""
fi
export TLA2TOOLS
[[ -n "${TLA2TOOLS:-}" ]] || echo "test-pstack: no tla2tools.jar — TLC tests will skip" >&2

run() {
    local label="$1" dir="$2"
    shift 2
    echo "== $label"
    ( cd "$dir" && "$@" ) || {
        echo "test-pstack: FAILED — $label" >&2
        status=1
    }
}

install_deps() {
    local dir="$1"
    [[ -d "$dir/node_modules" ]] && return 0
    echo "== installing dependencies in ${dir#"$REPO_ROOT"/}"
    ( cd "$dir" && bun install ) || {
        echo "test-pstack: bun install failed in $dir" >&2
        status=1
    }
}

install_deps "$STATECHART"
install_deps "$POTETO_MODE"

run "statechart (node --test)" "$STATECHART" \
    node --disable-warning=ExperimentalWarning --test test/*.test.ts
run "poteto-mode (bun test)" "$POTETO_MODE" \
    bun test watch-pr check-plan.test.ts
run "poteto-mode (tsc --strict)" "$POTETO_MODE" \
    ./node_modules/.bin/tsc --project watch-pr/tsconfig.json --noEmit --strict

if [[ $status -eq 0 ]]; then
    echo "test-pstack: OK"
else
    echo "test-pstack: FAILED" >&2
fi
exit "$status"
