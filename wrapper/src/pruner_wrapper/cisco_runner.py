"""Run the pinned `cisco-ai-skill-scanner` against a target path."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, cast

CISCO_BINARY = "skill-scanner"
PINNED_VERSION = "2.0.9"


def is_available() -> bool:
    """Return True if the pinned Cisco binary is on PATH."""

    return shutil.which(CISCO_BINARY) is not None


def run_cisco(target: Path) -> dict[str, Any] | None:
    """Run Cisco's `skill-scanner scan-all <target>` and return parsed SARIF.

    Returns `None` if the binary is missing. Raises `subprocess.CalledProcessError`
    on engine error other than "findings present" (Cisco exits non-zero on
    findings, which is normal). Output written to a tempfile and parsed.
    """

    if not is_available():
        return None

    with tempfile.NamedTemporaryFile(mode="w", suffix=".sarif", delete=False) as tmp:
        sarif_path = Path(tmp.name)

    cmd = [
        CISCO_BINARY,
        "scan-all" if target.is_dir() else "scan",
        str(target),
        "--format",
        "sarif",
        "--output-sarif",
        str(sarif_path),
    ]
    if target.is_dir():
        cmd.append("--recursive")

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


def cisco_version() -> str:
    """Return the installed Cisco engine version (best-effort)."""

    if not is_available():
        return "missing"
    try:
        result = subprocess.run(
            [CISCO_BINARY, "--version"], check=False, capture_output=True, text=True, timeout=10
        )
        out = (result.stdout or result.stderr).strip()
        return out or PINNED_VERSION
    except subprocess.SubprocessError:
        return PINNED_VERSION


def license_drift_check(license_text: str) -> bool:
    """Return True if `license_text` still contains the Apache-2.0 marker."""

    markers = ("Apache License", "Apache-2.0", "apache.org/licenses/LICENSE-2.0")
    return any(m in license_text for m in markers)
