"""Tests for pack_runner — load + dispatch + scope + downgrade."""

from __future__ import annotations

from pathlib import Path

import pytest

from pruner_wrapper.pack_runner import (
    file_matches_scope,
    filter_by_threshold,
    load_pack,
    load_rule,
    scan_rule_against_text,
    scan_tree,
)
from pruner_wrapper.types import Finding, Location, Rule


def _write_rule(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "X-1.yml"
    p.write_text(body, encoding="utf-8")
    return p


def test_load_rule_minimal(tmp_path: Path) -> None:
    body = (
        "id: X-1\n"
        "slug: x\n"
        "title: t\n"
        "severity: high\n"
        "category: prompt-injection\n"
        "owasp_ref: LLM01\n"
        "owasp_ast: AST01\n"
        "pattern:\n"
        "  type: regex\n"
        "  value: hit\n"
        "rationale: |\n"
        "  Long rationale describing the rule's reason.\n"
        "fixtures:\n"
        "  positive: ['hit']\n"
        "  negative: ['miss']\n"
        "scope:\n"
        "  file_patterns: ['**/*.md']\n"
        "status: stable\n"
        "since: '0.1.0'\n"
    )
    rule = load_rule(_write_rule(tmp_path, body))
    assert rule.id == "X-1"
    assert rule.severity == "high"


def test_load_rule_missing_keys_raises(tmp_path: Path) -> None:
    body = "id: X-1\n"
    with pytest.raises(ValueError):
        load_rule(_write_rule(tmp_path, body))


def test_load_pack_walks_yaml(tmp_path: Path) -> None:
    rules_root = tmp_path / "rules"
    rules_root.mkdir()
    body = (
        "id: A\nslug: a\ntitle: t\nseverity: low\ncategory: integrity\n"
        "pattern: {type: regex, value: x}\nrationale: 'reason long enough.'\n"
        "fixtures: {positive: [], negative: []}\n"
        "scope: {file_patterns: ['**/*.md']}\n"
        "status: stable\nsince: '0.1.0'\n"
    )
    (rules_root / "a.yml").write_text(body, encoding="utf-8")
    rules = load_pack(rules_root)
    assert len(rules) == 1
    assert rules[0].id == "A"


def test_load_pack_empty_dir(tmp_path: Path) -> None:
    rules_root = tmp_path / "rules"
    rules_root.mkdir()
    assert load_pack(rules_root) == []


def test_load_pack_missing_dir(tmp_path: Path) -> None:
    assert load_pack(tmp_path / "missing") == []


def test_file_matches_scope_glob() -> None:
    assert file_matches_scope("skills/foo/SKILL.md", ["skills/*/SKILL.md"])
    assert file_matches_scope("skills/foo/scripts/x.py", ["skills/**/scripts/**"])
    assert not file_matches_scope("docs/x.md", ["skills/*/SKILL.md"])


def test_filter_by_threshold() -> None:
    f_high = Finding(
        id="X", category="prompt-injection", severity_declared="high",
        severity_effective="high", tool="t", location=Location(path="a.md"), message="m",
    )
    f_low = Finding(
        id="Y", category="prompt-injection", severity_declared="low",
        severity_effective="low", tool="t", location=Location(path="a.md"), message="m",
    )
    kept = filter_by_threshold([f_high, f_low], "medium")
    assert kept == [f_high]


def test_scan_tree_matches_scope(tmp_path: Path) -> None:
    rule = Rule(
        id="X-1",
        slug="x",
        title="t",
        severity="high",
        category="prompt-injection",
        pattern={"type": "regex", "value": "hit"},
        rationale="r",
        fixtures={"positive": [], "negative": []},
        scope={"file_patterns": ["**/*.md"]},
        status="stable",
        since="0.1.0",
    )
    (tmp_path / "a.md").write_text("hit\n")
    (tmp_path / "b.py").write_text("hit\n")
    findings = scan_tree(root=tmp_path, rules=[rule])
    assert len(findings) == 1
    assert findings[0].location.path == "a.md"


def test_scan_tree_pd_gating(tmp_path: Path) -> None:
    pd_rule = Rule(
        id="PD-X",
        slug="x",
        title="t",
        severity="medium",
        category="prompt-defense",
        pattern={
            "type": "absence-regex",
            "must_contain_any": ["refuse"],
        },
        rationale="r",
        fixtures={"positive": [], "negative": []},
        scope={"file_patterns": ["**/*.md"]},
        status="stable",
        since="0.1.0",
        default_active=False,
    )
    (tmp_path / "a.md").write_text("---\nname: x\ndescription: 'agent that plans'\n---\nbody")
    findings_off = scan_tree(root=tmp_path, rules=[pd_rule], scan_prompt_defense=False)
    assert findings_off == []
    findings_on = scan_tree(root=tmp_path, rules=[pd_rule], scan_prompt_defense=True)
    assert len(findings_on) == 1


def test_scan_rule_against_text() -> None:
    rule = Rule(
        id="X",
        slug="x",
        title="t",
        severity="high",
        category="prompt-injection",
        pattern={"type": "regex", "value": "hit"},
        rationale="r",
        fixtures={"positive": [], "negative": []},
        scope={"file_patterns": ["**/*.md"]},
        status="stable",
        since="0.1.0",
    )
    findings = scan_rule_against_text(rule, "hit me\n")
    assert len(findings) == 1
