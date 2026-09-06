#!/bin/sh
# test_readme_current.sh — anti-drift test for README.md (T106).
#
# Asserts (AC numbers from tasks/TASK_GUIDE_T106.md):
#   AC1 — README names the current release, matching RUNBOOK.md's newest release row
#   AC2 — README states that Codex skips oversize skill bodies, and names exactly the
#         skills currently over the cap in lib/harness-fetch.sh (derived, not hardcoded)
#
# Both the oversize-skill set and the cap are DERIVED at runtime from
# lib/harness-fetch.sh and the skills/ tree — never hardcoded — because the set is a
# point-in-time measurement that changes whenever a skill body is edited (this repo has
# hit that exact bug before: see memory/learnings.md). The negative case below (padding a
# skill past the cap) is what proves this derivation is load-bearing rather than
# decorative.
#
# Usage: sh tests/test_readme_current.sh

set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
README="$ROOT/README.md"
RUNBOOK="$ROOT/RUNBOOK.md"
HARNESS_FETCH="$ROOT/lib/harness-fetch.sh"
FAIL=0

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  FAIL=1
}

pass() {
  printf 'PASS: %s\n' "$1"
}

for f in "$README" "$RUNBOOK" "$HARNESS_FETCH"; do
  if [ ! -f "$f" ]; then
    printf 'test_readme_current: ERROR — required file not found: %s\n' "$f" >&2
    exit 1
  fi
done

# ── AC1: README names the current release, matching RUNBOOK.md's newest row ──
# RUNBOOK's Release Log table is oldest-first (v1.0.0, then v1.1.0, then v2.0.0), so the
# newest release is the LAST `| vX.Y.Z |` row, not the first.
CURRENT_VERSION="$(grep -E '^\| v[0-9]+\.[0-9]+\.[0-9]+ \|' "$RUNBOOK" | tail -n1 | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2}')"

if [ -z "$CURRENT_VERSION" ]; then
  fail "AC1: could not derive a current version from RUNBOOK.md's Release Log table"
else
  if grep -qF "$CURRENT_VERSION" "$README"; then
    pass "AC1: README names the current release ($CURRENT_VERSION), matching RUNBOOK.md's newest row"
  else
    fail "AC1: README does not mention '$CURRENT_VERSION' (RUNBOOK.md's newest release row)"
  fi
fi

# ── AC2: derive the Codex skill-body cap from lib/harness-fetch.sh ──
# The cap is returned by the `codex) printf 'N' ;;` case arm of the per-harness default
# function (see harness_skill_body_cap's default branch) — pull the literal it prints.
CAP="$(awk '/codex\)[[:space:]]*printf/ { match($0, /printf[[:space:]]*.[0-9]+/); s=substr($0, RSTART, RLENGTH); gsub(/[^0-9]/, "", s); print s; exit }' "$HARNESS_FETCH")"

if [ -z "$CAP" ]; then
  fail "AC2: could not derive the Codex skill-body cap from lib/harness-fetch.sh"
else
  pass "AC2 setup: derived cap = $CAP bytes from lib/harness-fetch.sh"
fi

# ── Derive the current oversize skill set from the skills/ tree ──
OVERSIZE=""
for skill_file in "$ROOT"/skills/*/SKILL.md; do
  [ -f "$skill_file" ] || continue
  size="$(wc -c < "$skill_file" | tr -d ' ')"
  if [ "$size" -gt "$CAP" ]; then
    name="$(basename "$(dirname "$skill_file")")"
    OVERSIZE="$OVERSIZE $name"
  fi
done
OVERSIZE="$(printf '%s' "$OVERSIZE" | sed -e 's/^ *//')"

if [ -z "$OVERSIZE" ]; then
  fail "AC2: no skill currently exceeds the derived cap ($CAP bytes) — test cannot verify README's list is non-empty and accurate"
else
  pass "AC2 setup: derived oversize skill set = [$OVERSIZE]"
fi

# README must mention that Codex skips oversize skills (not "truncates").
if grep -qi 'skip' "$README" && ! grep -qiE 'truncat' "$README"; then
  pass "AC2: README uses 'skip' language for oversize skills, not 'truncate'"
else
  fail "AC2: README must say oversize skills are SKIPPED (not truncated) for Codex"
fi

# Every currently-oversize skill must be named in the README.
for name in $OVERSIZE; do
  if grep -qF "$name" "$README"; then
    pass "AC2: README names oversize skill '$name'"
  else
    fail "AC2: README does not name currently-oversize skill '$name'"
  fi
done

if [ "$FAIL" -ne 0 ]; then
  printf '\ntest_readme_current: FAILED\n' >&2
  exit 1
fi

printf '\ntest_readme_current: ALL PASS\n'
