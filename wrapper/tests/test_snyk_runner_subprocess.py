"""Subprocess-mocking tests for the Snyk runner."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from pruner_wrapper import snyk_runner


def test_run_snyk_missing_binary(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(snyk_runner, "is_available", lambda: False)
    monkeypatch.setattr(snyk_runner, "is_authorised", lambda: True)
    assert snyk_runner.run_snyk(tmp_path) is None


def test_run_snyk_unauthorised(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(snyk_runner, "is_available", lambda: True)
    monkeypatch.setattr(snyk_runner, "is_authorised", lambda: False)
    assert snyk_runner.run_snyk(tmp_path) is None


def test_run_snyk_writes_and_parses_sarif(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(snyk_runner, "is_available", lambda: True)
    monkeypatch.setattr(snyk_runner, "is_authorised", lambda: True)
    sarif = {"version": "2.1.0", "runs": []}

    def fake_run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        # find the --sarif-file-output=PATH argument
        for arg in cmd:
            if arg.startswith("--sarif-file-output="):
                out = Path(arg.split("=", 1)[1])
                out.write_text(json.dumps(sarif), encoding="utf-8")
                break
        return subprocess.CompletedProcess(args=cmd, returncode=0)

    monkeypatch.setattr(snyk_runner.subprocess, "run", fake_run)
    parsed = snyk_runner.run_snyk(tmp_path)
    assert parsed == sarif


def test_run_snyk_timeout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(snyk_runner, "is_available", lambda: True)
    monkeypatch.setattr(snyk_runner, "is_authorised", lambda: True)

    def boom(*_args: Any, **_kwargs: Any) -> None:
        raise subprocess.TimeoutExpired(cmd="x", timeout=1)

    monkeypatch.setattr(snyk_runner.subprocess, "run", boom)
    assert snyk_runner.run_snyk(tmp_path) is None


def test_run_snyk_invalid_sarif(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(snyk_runner, "is_available", lambda: True)
    monkeypatch.setattr(snyk_runner, "is_authorised", lambda: True)

    def fake_run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        for arg in cmd:
            if arg.startswith("--sarif-file-output="):
                Path(arg.split("=", 1)[1]).write_text("not json", encoding="utf-8")
                break
        return subprocess.CompletedProcess(args=cmd, returncode=0)

    monkeypatch.setattr(snyk_runner.subprocess, "run", fake_run)
    assert snyk_runner.run_snyk(tmp_path) is None
