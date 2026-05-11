"""Tests for the pruner CLI surface."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pruner_wrapper.cli import (
    EXIT_FINDINGS_ABOVE,
    EXIT_FINDINGS_BELOW,
    EXIT_INTERNAL,
    EXIT_OK,
    main,
)


def test_help_prints_and_exits(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0


def test_version_prints_and_exits(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0


def test_scan_missing_path_returns_internal_error(tmp_path: Path) -> None:
    code = main(["scan", str(tmp_path / "absent")])
    assert code == EXIT_INTERNAL


def test_scan_clean_examples_benign(repo_root: Path) -> None:
    benign = repo_root / "examples" / "benign-skill"
    code = main(["scan", str(benign), "--without-cisco", "--format", "json", "--output",
                 str(repo_root / ".pruner" / "benign.report.json"),
                 "--rules", str(repo_root / "rules"),
                 "--target-repo", "<test>"])
    # benign-skill should produce zero findings, exit OK
    assert code in (EXIT_OK, EXIT_FINDINGS_BELOW)


def test_compose_invokes_and_writes(tmp_path: Path, repo_root: Path) -> None:
    sarif = {
        "version": "2.1.0",
        "runs": [
            {
                "tool": {"driver": {"name": "pruner-wrapper", "version": "0.2.0"}},
                "results": [],
            }
        ],
    }
    p = tmp_path / "in.sarif"
    p.write_text(json.dumps(sarif), encoding="utf-8")
    out = tmp_path / "report.json"
    code = main(["compose", "--inputs", str(p), "--output", str(out),
                 "--target-repo", "<test>"])
    assert code == EXIT_OK
    assert out.exists()
    parsed = json.loads(out.read_text())
    assert parsed["schema_version"] == "1.0.0"


def test_badge_writes_svg(tmp_path: Path) -> None:
    report = {
        "summary": {"grade": "A"},
        "tools": [{"name": "cisco-ai-skill-scanner", "version": "2.0.11"}],
    }
    rpath = tmp_path / "r.json"
    rpath.write_text(json.dumps(report), encoding="utf-8")
    out = tmp_path / "b.svg"
    code = main(["badge", "--report", str(rpath), "--output", str(out)])
    assert code == EXIT_OK
    svg = out.read_text(encoding="utf-8")
    assert "Grade A" in svg


def test_gate_clean(tmp_path: Path) -> None:
    report = {"findings": []}
    rpath = tmp_path / "r.json"
    rpath.write_text(json.dumps(report), encoding="utf-8")
    code = main(["gate", "--report", str(rpath), "--fail-on", "critical"])
    assert code == EXIT_OK


def test_gate_above_threshold(tmp_path: Path) -> None:
    report = {
        "findings": [
            {
                "id": "X",
                "category": "prompt-injection",
                "severity_declared": "critical",
                "severity_effective": "critical",
                "tool": "pruner-wrapper",
                "location": {"path": "a.md"},
                "message": "m",
            }
        ]
    }
    rpath = tmp_path / "r.json"
    rpath.write_text(json.dumps(report), encoding="utf-8")
    code = main(["gate", "--report", str(rpath), "--fail-on", "high"])
    assert code == EXIT_FINDINGS_ABOVE
