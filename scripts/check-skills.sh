#!/usr/bin/env bash
# Structure checks for the skills in this repo.
#
# Rules:
#   1. Every skill directory has a SKILL.md with valid frontmatter:
#      a `name` that matches the directory, and a `description`.
#   2. Relative links inside SKILL.md point at files that exist.
#   3. Every skill directory is either tracked by git or mirrored in the
#      autolearn persona home (~/.autolearn/personas/default/skills/<name>).
#      Rule 3 is what keeps a local-only skill from existing in exactly one
#      unversioned place, where `git clean -fd` would delete it.
#
# Usage: scripts/check-skills.sh [skill-dir ...]
#        no args → every top-level directory with a SKILL.md
#
# Exit 0 = all rules pass. Exit 1 = at least one violation.

set -uo pipefail

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PERSONA_HOME="${PERSONA_HOME:-$HOME/.autolearn/personas/default/skills}"
cd "$REPO_ROOT" || exit 1

violations=0
notes=0

fail() { printf 'structure-check: FAIL %s\n' "$1"; violations=$((violations + 1)); }
note() { printf 'structure-check: note %s\n' "$1"; notes=$((notes + 1)); }

# Frontmatter fields of a SKILL.md: name and description, from the YAML block
# between the first two --- lines.
frontmatter_value() {
  local file=$1 field=$2
  awk -v field="$field" '
    NR == 1 && $0 != "---" { exit }
    NR == 1 { inblock = 1; next }
    inblock && $0 == "---" { exit }
    inblock {
      line = $0
      sub(/^[ \t]+/, "", line)
      if (index(line, field ":") == 1) {
        value = substr(line, length(field) + 2)
        sub(/^[ \t]+/, "", value)
        sub(/[ \t]+$/, "", value)
        gsub(/^"|"$/, "", value)
        print value
        exit
      }
    }
  ' "$file"
}

# --- Rule 1: frontmatter ---------------------------------------------------
# --- Rule 2: relative links ------------------------------------------------
# --- Rule 3: tracked or mirrored -------------------------------------------
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

for skill in "${skills[@]}"; do
  file="$skill/SKILL.md"
  if [ ! -f "$file" ]; then
    fail "$skill: no SKILL.md"
    continue
  fi

  name=$(frontmatter_value "$file" "name")
  description=$(frontmatter_value "$file" "description")

  if [ -z "$name" ]; then
    fail "$file: frontmatter has no 'name'"
  elif [ "$name" != "$skill" ]; then
    fail "$file: frontmatter name '$name' does not match directory '$skill'"
  fi

  if [ -z "$description" ]; then
    fail "$file: frontmatter has no 'description'"
  fi

  # Rule 2: relative markdown links and backticked paths that look like files.
  while IFS= read -r target; do
    [ -n "$target" ] || continue
    case "$target" in
      http*|mailto:*|"#"*) continue ;;
    esac
    resolved="$skill/${target%%#*}"
    if [ ! -e "$resolved" ]; then
      fail "$file: relative link '$target' does not exist"
    fi
  done < <(grep -oE '\]\(([^)]+)\)' "$file" 2>/dev/null | sed -E 's/^\]\((.*)\)$/\1/')

  # Rule 3: versioned or mirrored.
  if ! git ls-files --error-unmatch "$skill" >/dev/null 2>&1; then
    if [ -d "$PERSONA_HOME/$skill" ]; then
      note "$skill: not tracked by git (mirrored in $PERSONA_HOME)"
    else
      fail "$skill: not tracked by git and not mirrored in $PERSONA_HOME — one copy of this skill would be lost on 'git clean -fd'"
    fi
  fi
done

if [ "$violations" -gt 0 ]; then
  printf 'structure-check: %d violation(s), %d note(s)\n' "$violations" "$notes"
  exit 1
fi

printf 'structure-check: OK (%d skill(s), %d note(s))\n' "${#skills[@]}" "$notes"
exit 0
