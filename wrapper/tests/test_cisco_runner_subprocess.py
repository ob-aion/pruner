"""Subprocess-mocking tests for the Cisco runner."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from pruner_wrapper import cisco_runner


def test_run_cisco_missing_binary(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cisco_runner, "is_available", lambda: False)
    assert cisco_runner.run_cisco(tmp_path) is None


def test_run_cisco_writes_and_parses_sarif(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(cisco_runner, "is_available", lambda: True)
    sarif = {"version": "2.1.0", "runs": []}

    def fake_run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        # Locate --output-sarif <path> in the args
        idx = cmd.index("--output-sarif")
        out = Path(cmd[idx + 1])
        out.write_text(json.dumps(sarif), encoding="utf-8")
        return subprocess.CompletedProcess(args=cmd, returncode=0)

    monkeypatch.setattr(cisco_runner.subprocess, "run", fake_run)
    target = tmp_path / "skills"
    target.mkdir()
    parsed = cisco_runner.run_cisco(target)
    assert parsed == sarif


def test_run_cisco_timeout_returns_none(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(cisco_runner, "is_available", lambda: True)

    def boom(*_args: Any, **_kwargs: Any) -> None:
        raise subprocess.TimeoutExpired(cmd="x", timeout=1)

    monkeypatch.setattr(cisco_runner.subprocess, "run", boom)
    assert cisco_runner.run_cisco(tmp_path) is None


def test_run_cisco_invalid_sarif(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cisco_runner, "is_available", lambda: True)

    def fake_run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        idx = cmd.index("--output-sarif")
        Path(cmd[idx + 1]).write_text("not json", encoding="utf-8")
        return subprocess.CompletedProcess(args=cmd, returncode=0)

    monkeypatch.setattr(cisco_runner.subprocess, "run", fake_run)
    assert cisco_runner.run_cisco(tmp_path) is None


def test_cisco_version_returns_string(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cisco_runner, "is_available", lambda: False)
    assert cisco_runner.cisco_version() == "missing"


def test_cisco_version_subprocess_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cisco_runner, "is_available", lambda: True)

    def boom(*_args: Any, **_kwargs: Any) -> None:
        raise subprocess.SubprocessError("nope")

    monkeypatch.setattr(cisco_runner.subprocess, "run", boom)
    assert cisco_runner.cisco_version() == cisco_runner.PINNED_VERSION
