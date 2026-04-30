#!/usr/bin/env bash
# Install the pinned cisco-ai-skill-scanner and verify Apache-2.0 marker.
# Halts with the lore-tagged drift message on license drift.
#
# Used by the composite action (action.yml) and runnable locally.

set -euo pipefail

PINNED_VERSION="${PRUNER_CISCO_VERSION:-2.0.9}"
APACHE_MARKERS=(
    "Apache License"
    "Apache-2.0"
    "apache.org/licenses/LICENSE-2.0"
)

echo "Loom thread engaged: cisco-ai-skill-scanner@${PINNED_VERSION}"

if ! command -v pip >/dev/null 2>&1; then
    echo "Temporal deviation in configuration. The Loom cannot run." >&2
    echo "  pip is missing — install Python 3.10+ first." >&2
    exit 3
fi

# Idempotent install. Use a venv if PRUNER_CISCO_VENV is set.
if [[ -n "${PRUNER_CISCO_VENV:-}" ]]; then
    if [[ ! -d "${PRUNER_CISCO_VENV}" ]]; then
        python3 -m venv "${PRUNER_CISCO_VENV}"
    fi
    # shellcheck disable=SC1091
    source "${PRUNER_CISCO_VENV}/bin/activate"
fi

pip install --quiet "cisco-ai-skill-scanner==${PINNED_VERSION}"

# Locate the installed LICENSE file.
LICENSE_PATH="$(python3 - <<'PY'
import importlib.metadata as md
import pathlib, sys
try:
    files = md.files("cisco-ai-skill-scanner")
except md.PackageNotFoundError:
    sys.exit(1)
if not files:
    sys.exit(1)
for f in files:
    name = pathlib.Path(str(f)).name
    if name == "LICENSE":
        print(f.locate())
        sys.exit(0)
sys.exit(1)
PY
)"

if [[ -z "${LICENSE_PATH}" || ! -f "${LICENSE_PATH}" ]]; then
    echo "Temporal deviation in upstream. Engine license drifted; halt." >&2
    echo "  Reason: LICENSE file not present in installed package metadata." >&2
    exit 3
fi

# Grep for any of the Apache markers.
matched=0
for marker in "${APACHE_MARKERS[@]}"; do
    if grep -q -F "${marker}" "${LICENSE_PATH}"; then
        matched=1
        break
    fi
done

if [[ "${matched}" -eq 0 ]]; then
    echo "Temporal deviation in upstream. Engine license drifted; halt." >&2
    echo "  Reason: Apache-2.0 marker missing from ${LICENSE_PATH}." >&2
    exit 3
fi

echo "License verified Apache-2.0 at ${LICENSE_PATH}."
