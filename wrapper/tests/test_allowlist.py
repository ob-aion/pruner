"""Tests for the allowlist parser + apply."""

from __future__ import annotations

from pathlib import Path

import pytest

from pruner_wrapper.allowlist import AllowlistError, apply_allowlist, load_allowlist
from pruner_wrapper.types import AllowlistEntry, Finding, Location


def _f(rule: str, path: str) -> Finding:
    return Finding(
        id=rule,
        category="prompt-injection",
        severity_declared="critical",
        severity_effective="critical",
        tool="pruner-wrapper",
        location=Location(path=path, line=1, start_column=1, end_column=2),
        message="m",
    )


def test_load_missing_file_returns_empty(tmp_path: Path) -> None:
    assert load_allowlist(tmp_path / "absent.yml") == []


def test_load_none_returns_empty() -> None:
    assert load_allowlist(None) == []


def test_load_valid(tmp_path: Path) -> None:
    p = tmp_path / "ig.yml"
    p.write_text(
        "version: 1\n"
        "ignores:\n"
        "  - rule: PI-UNI-001\n"
        "    path: docs/x.md\n"
        "    justification: test fixture\n",
        encoding="utf-8",
    )
    entries = load_allowlist(p)
    assert len(entries) == 1
    assert entries[0].rule == "PI-UNI-001"
    assert entries[0].justification == "test fixture"


def test_missing_justification_rejected(tmp_path: Path) -> None:
    p = tmp_path / "ig.yml"
    p.write_text(
        "version: 1\n"
        "ignores:\n"
        "  - rule: PI-UNI-001\n"
        "    path: docs/x.md\n"
        "    justification: \"\"\n",
        encoding="utf-8",
    )
    with pytest.raises(AllowlistError):
        load_allowlist(p)


def test_unknown_version_rejected(tmp_path: Path) -> None:
    p = tmp_path / "ig.yml"
    p.write_text("version: 99\nignores: []\n", encoding="utf-8")
    with pytest.raises(AllowlistError):
        load_allowlist(p)


def test_top_level_must_be_mapping(tmp_path: Path) -> None:
    p = tmp_path / "ig.yml"
    p.write_text("- not a mapping\n", encoding="utf-8")
    with pytest.raises(AllowlistError):
        load_allowlist(p)


def test_apply_allowlist_suppresses() -> None:
    findings = [_f("R-1", "docs/x.md"), _f("R-2", "skills/foo/SKILL.md")]
    entries = [AllowlistEntry(rule="R-1", path="docs/**", justification="example")]
    kept, applied = apply_allowlist(findings, entries)
    assert len(kept) == 1
    assert kept[0].id == "R-2"
    assert len(applied) == 1


def test_apply_empty_allowlist_passes_through() -> None:
    findings = [_f("R", "skills/a/SKILL.md")]
    kept, applied = apply_allowlist(findings, [])
    assert kept == findings
    assert applied == []
