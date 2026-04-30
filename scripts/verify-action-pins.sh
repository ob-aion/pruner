#!/usr/bin/env bash
# Verify every SHA-pinned `uses:` line in this repo's workflows and the
# composite action resolves to a real commit in the upstream repository.
#
# OpenSSF Scorecard's webapp validates that pinned SHAs are real commits
# and rejects annotated-tag-object SHAs with a 400 / "imposter commit"
# error. Pinning to commit SHAs is the only stable form. See
# docs/sha-pinning.md for the gotcha and how to resolve a tag-object to
# its underlying commit.
#
# Usage: bash scripts/verify-action-pins.sh
# Exit codes: 0 = all pins resolve to commits; 1 = bad pin; 2 = missing gh.

set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "FATAL: gh CLI required (https://cli.github.com/)" >&2
  exit 2
fi

cd "$(git rev-parse --show-toplevel)"

shopt -s nullglob
FILES=( .github/workflows/*.yml action.yml )

RC=0
PASS=0
FAIL=0

while IFS= read -r line; do
  FILE="${line%%:*}"
  REMAINDER="${line#*:}"
  LINENO_FOUND="${REMAINDER%%:*}"
  CONTENT="${REMAINDER#*:}"

  REF=$(printf '%s\n' "$CONTENT" | sed -nE 's/.*uses:[[:space:]]+([^@[:space:]]+)@([a-f0-9]{40}).*/\1 \2/p')
  [ -n "$REF" ] || continue

  REPO_PATH="${REF% *}"
  SHA="${REF#* }"
  OWNER_REPO=$(printf '%s\n' "$REPO_PATH" | awk -F/ '{print $1"/"$2}')

  if gh api "repos/${OWNER_REPO}/commits/${SHA}" --jq '.sha' >/dev/null 2>&1; then
    printf 'OK    %s@%s  (%s:%s)\n' "$OWNER_REPO" "$SHA" "$FILE" "$LINENO_FOUND"
    PASS=$((PASS + 1))
  else
    printf 'BAD   %s@%s  (%s:%s) — not a commit (likely tag-object SHA)\n' \
      "$OWNER_REPO" "$SHA" "$FILE" "$LINENO_FOUND" >&2
    FAIL=$((FAIL + 1))
    RC=1
  fi
done < <(grep -nHE 'uses:[[:space:]]+[^/]+/[^@]+@[a-f0-9]{40}' "${FILES[@]}" 2>/dev/null || true)

printf '\n%d pin(s) verified, %d failure(s).\n' "$PASS" "$FAIL"
exit "${RC}"
