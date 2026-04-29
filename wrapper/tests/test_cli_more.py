"""More CLI tests to cover scan paths."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pruner_wrapper import cisco_runner, cli
from pruner_wrapper.cli import EXIT_INTERNAL, EXIT_OK, main


def _disable_cisco(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cisco_runner, "is_available", lambda: False)


def test_scan_terminal_format(
    tmp_path: Path, repo_root: Path, capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _disable_cisco(monkeypatch)
    benign = repo_root / "examples" / "benign-skill"
    code = main(["scan", str(benign), "--without-cisco", "--rules", str(repo_root / "rules")])
    out = capsys.readouterr().out
    assert "Pruning variants at threshold" in out
    assert code == EXIT_OK


def test_scan_sarif_format(tmp_path: Path, repo_root: Path,
                           monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_cisco(monkeypatch)
    benign = repo_root / "examples" / "benign-skill"
    out = tmp_path / "report.sarif"
    code = main(["scan", str(benign), "--without-cisco", "--rules", str(repo_root / "rules"),
                 "--format", "sarif", "--output", str(out)])
    assert code == EXIT_OK
    sarif = json.loads(out.read_text(encoding="utf-8"))
    assert sarif["version"] == "2.1.0"


def test_scan_json_to_stdout(repo_root: Path, capsys: pytest.CaptureFixture[str],
                              monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_cisco(monkeypatch)
    benign = repo_root / "examples" / "benign-skill"
    code = main(["scan", str(benign), "--without-cisco", "--rules", str(repo_root / "rules"),
                 "--format", "json"])
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert parsed["schema_version"] == "1.0.0"
    assert code == EXIT_OK


def test_scan_invalid_policy(tmp_path: Path, repo_root: Path,
                              monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_cisco(monkeypatch)
    benign = repo_root / "examples" / "benign-skill"
    bad_policy = tmp_path / "bad.yml"
    bad_policy.write_text("version: 99\nname: bad\n", encoding="utf-8")
    code = main(["scan", str(benign), "--without-cisco", "--policy", str(bad_policy),
                 "--rules", str(repo_root / "rules")])
    assert code == EXIT_INTERNAL


def test_scan_invalid_allowlist(tmp_path: Path, repo_root: Path,
                                  monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_cisco(monkeypatch)
    benign = repo_root / "examples" / "benign-skill"
    bad_al = tmp_path / "bad.yml"
    bad_al.write_text("version: 1\nignores:\n  - rule: X\n    path: y\n    justification: ''\n",
                      encoding="utf-8")
    code = main(["scan", str(benign), "--without-cisco", "--allowlist", str(bad_al),
                 "--rules", str(repo_root / "rules")])
    assert code == EXIT_INTERNAL


def test_compose_with_invalid_input(tmp_path: Path) -> None:
    bad = tmp_path / "bad.sarif"
    bad.write_text("not json", encoding="utf-8")
    out = tmp_path / "report.json"
    code = main(["compose", "--inputs", str(bad), "--output", str(out)])
    assert code == EXIT_OK
    assert json.loads(out.read_text())["summary"]["total"] == 0


def test_engine_sha_from_tools_helper() -> None:
    short = cli._engine_sha_from_tools(
        [{"name": "cisco-ai-skill-scanner", "version": "2.0.9", "sha": "abcdef0123"}]
    )
    assert short == "abcdef01"


def test_engine_sha_falls_back() -> None:
    short = cli._engine_sha_from_tools([])
    assert short == cli.CISCO_PINNED_VERSION
