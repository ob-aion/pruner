#!/usr/bin/env bash
# Bundle the report artefacts into pruner-report.zip for release upload.
# Used by .github/workflows/release.yml.

set -euo pipefail

OUT_DIR="${1:-./.pruner}"
BUNDLE="${OUT_DIR}/pruner-report.zip"

cd "${OUT_DIR}"
[[ -f report.json ]] || { echo "report.json missing" >&2; exit 3; }

artefacts=(report.json)
for f in *.sarif; do [[ -e "${f}" ]] && artefacts+=("${f}"); done
for f in sbom.cdx.json scorecard.json badge.svg attestation.intoto.jsonl; do
    [[ -e "${f}" ]] && artefacts+=("${f}")
done

zip -q -j "$(basename "${BUNDLE}")" "${artefacts[@]}"
echo "Bundle written: ${BUNDLE}"
