"""Optional second-opinion runner for `snyk/agent-scan`.

Disabled by default. Activated when `SNYK_TOKEN` env var is present and the
caller passes `--with-snyk`. Output is non-blocking; merged into the report
under `tools[]` with `mode: second-opinion`, `blocking: false`.

Important: `snyk/agent-scan` uplinks scan content to Snyk cloud. The composite
action surfaces this fact in the report explicitly so consumers can opt out
on private/regulated content.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, cast

SNYK_BINARY = "snyk"


def is_available() -> bool:
    """Return True if the snyk CLI is installed."""

    return shutil.which(SNYK_BINARY) is not None


def is_authorised() -> bool:
    """Return True if a SNYK_TOKEN is present in the environment."""

    return bool(os.environ.get("SNYK_TOKEN"))


def run_snyk(target: Path) -> dict[str, Any] | None:
    """Invoke `snyk agent-scan` against `target`. Returns SARIF dict or None."""

    if not is_available() or not is_authorised():
        return None

    with tempfile.NamedTemporaryFile(mode="w", suffix=".sarif", delete=False) as tmp:
        sarif_path = Path(tmp.name)

    cmd = [
        SNYK_BINARY,
        "agent-scan",
        str(target),
        "--sarif-file-output=" + str(sarif_path),
    ]
    try:
        subprocess.run(cmd, check=False, capture_output=True, timeout=600)
    except subprocess.TimeoutExpired:
        return None

    if not sarif_path.exists() or sarif_path.stat().st_size == 0:
        return None

    try:
        return cast(dict[str, Any], json.loads(sarif_path.read_text(encoding="utf-8")))
    except json.JSONDecodeError:
        return None
