#!/usr/bin/env bash
# Compose the aggregated report-v1 bundle from all SARIFs in .pruner/.
# Used by the composite action.

set -euo pipefail

OUT_DIR="${1:-./.pruner}"
mkdir -p "${OUT_DIR}"

INPUTS=()
for f in "${OUT_DIR}"/*.sarif; do
    [[ -e "${f}" ]] && INPUTS+=("${f}")
done

if [[ "${#INPUTS[@]}" -eq 0 ]]; then
    echo "No SARIF inputs found in ${OUT_DIR}" >&2
    exit 3
fi

POLICY_ARG=()
[[ -f .pruner-policy.yml ]] && POLICY_ARG=(--policy .pruner-policy.yml)

ALLOWLIST_ARG=()
[[ -f .pruner-ignore.yml ]] && ALLOWLIST_ARG=(--allowlist .pruner-ignore.yml)

pruner compose \
    --inputs "${INPUTS[@]}" \
    --output "${OUT_DIR}/report.json" \
    "${POLICY_ARG[@]}" \
    "${ALLOWLIST_ARG[@]}" \
    --target-repo "${GITHUB_REPOSITORY:-<local>}" \
    --target-commit "${GITHUB_SHA:-}"

echo "Report written: ${OUT_DIR}/report.json"
