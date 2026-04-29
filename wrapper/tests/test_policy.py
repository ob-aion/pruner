"""Tests for the policy loader + evaluator."""

from __future__ import annotations

from pathlib import Path

import pytest

from pruner_wrapper.policy import PolicyError, evaluate, load_policy, severity_satisfies
from pruner_wrapper.types import AllowlistEntry, Finding, Location, ToolEntry


def test_load_returns_none_when_path_absent(tmp_path: Path) -> None:
    assert load_policy(tmp_path / "absent.yml") is None
    assert load_policy(None) is None


def test_load_valid(tmp_path: Path) -> None:
    p = tmp_path / "policy.yml"
    p.write_text(
        "version: 1\n"
        "name: 'Org Policy'\n"
        "min_score: 80\n"
        "max_severity: high\n",
        encoding="utf-8",
    )
    pol = load_policy(p)
    assert pol is not None
    assert pol.name == "Org Policy"
    assert pol.min_score == 80


def test_load_missing_name_raises(tmp_path: Path) -> None:
    p = tmp_path / "policy.yml"
    p.write_text("version: 1\n", encoding="utf-8")
    with pytest.raises(PolicyError):
        load_policy(p)


def test_load_unknown_version_raises(tmp_path: Path) -> None:
    p = tmp_path / "policy.yml"
    p.write_text("version: 99\nname: x\n", encoding="utf-8")
    with pytest.raises(PolicyError):
        load_policy(p)


def test_evaluate_with_no_policy_compliant() -> None:
    out = evaluate(
        None, findings=[], allowlisted=[], tools=[], score=100, target_paths=[]
    )
    assert out["compliant"] is True
    assert out["violations"] == []


def test_evaluate_min_score_violation() -> None:
    from pruner_wrapper.types import Policy

    pol = Policy(name="x", min_score=90)
    out = evaluate(pol, findings=[], allowlisted=[], tools=[], score=85, target_paths=[])
    assert out["compliant"] is False
    assert out["violations"][0]["reason"] == "min_score"


def test_evaluate_max_severity_violation() -> None:
    from pruner_wrapper.types import Policy

    pol = Policy(name="x", max_severity="medium")
    finding = Finding(
        id="R", category="secrets", severity_declared="critical",
        severity_effective="critical", tool="pruner-wrapper",
        location=Location(path="a.md"), message="m",
    )
    out = evaluate(pol, findings=[finding], allowlisted=[], tools=[], score=100, target_paths=[])
    assert out["compliant"] is False


def test_evaluate_banned_rules_bypass() -> None:
    from pruner_wrapper.types import Policy

    pol = Policy(name="x", banned_rules_bypass=["PI-UNI-001"])
    entry = AllowlistEntry(rule="PI-UNI-001", path="docs/x.md", justification="t")
    out = evaluate(
        pol, findings=[], allowlisted=[entry], tools=[], score=100, target_paths=[]
    )
    assert out["compliant"] is False


def test_evaluate_required_scans() -> None:
    from pruner_wrapper.types import Policy

    pol = Policy(name="x", required_scans=["cisco"])
    out = evaluate(pol, findings=[], allowlisted=[], tools=[], score=100, target_paths=[])
    assert out["compliant"] is False
    assert out["violations"][0]["reason"] == "required_scans"


def test_evaluate_required_scans_satisfied() -> None:
    from pruner_wrapper.types import Policy

    pol = Policy(name="x", required_scans=["cisco"])
    tools = [ToolEntry(name="cisco-ai-skill-scanner", version="2.0.9", mode="primary")]
    out = evaluate(pol, findings=[], allowlisted=[], tools=tools, score=100, target_paths=[])
    assert out["compliant"] is True


def test_evaluate_forbidden_paths() -> None:
    from pruner_wrapper.types import Policy

    pol = Policy(name="x", forbidden_paths=["**/*.env"])
    out = evaluate(
        pol, findings=[], allowlisted=[], tools=[], score=100, target_paths=["secrets/.env"]
    )
    assert out["compliant"] is False


def test_severity_satisfies() -> None:
    assert severity_satisfies("critical", "high")
    assert not severity_satisfies("low", "high")
    assert severity_satisfies("medium", "medium")
