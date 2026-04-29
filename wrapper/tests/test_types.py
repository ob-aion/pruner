"""Tests for the core dataclasses."""

from __future__ import annotations

from pruner_wrapper.types import (
    SEVERITY_DEDUCTION,
    SEVERITY_RANK,
    SOURCE_CONFIDENCE_WEIGHT,
    AllowlistEntry,
    Finding,
    Location,
    Policy,
    Rule,
    ToolEntry,
)


def test_severity_rank_ordering() -> None:
    assert SEVERITY_RANK["info"] < SEVERITY_RANK["low"]
    assert SEVERITY_RANK["low"] < SEVERITY_RANK["medium"]
    assert SEVERITY_RANK["medium"] < SEVERITY_RANK["high"]
    assert SEVERITY_RANK["high"] < SEVERITY_RANK["critical"]


def test_severity_deductions() -> None:
    assert SEVERITY_DEDUCTION["critical"] == 25
    assert SEVERITY_DEDUCTION["high"] == 15
    assert SEVERITY_DEDUCTION["medium"] == 5
    assert SEVERITY_DEDUCTION["low"] == 2
    assert SEVERITY_DEDUCTION["info"] == 0


def test_source_confidence_weights() -> None:
    assert SOURCE_CONFIDENCE_WEIGHT["active-runtime"] == 1.00
    assert SOURCE_CONFIDENCE_WEIGHT["test-fixture"] == 0.25


def test_finding_to_dict_roundtrip() -> None:
    f = Finding(
        id="X-001",
        category="secrets",
        severity_declared="high",
        severity_effective="medium",
        tool="pruner-wrapper",
        location=Location(path="a.md", line=2, start_column=3, end_column=8),
        message="msg",
        owasp_ref="LLM05",
        owasp_ast="AST07",
        evidence_snippet="hint",
    )
    d = f.to_dict()
    assert d["id"] == "X-001"
    assert d["location"] == {"path": "a.md", "line": 2, "start_column": 3, "end_column": 8}
    assert d["owasp_ast"] == "AST07"


def test_location_to_dict_minimal() -> None:
    loc = Location(path="a.md")
    assert loc.to_dict() == {"path": "a.md"}


def test_rule_dataclass_defaults() -> None:
    rule = Rule(
        id="X-001",
        slug="x",
        title="t",
        severity="high",
        category="secrets",
        pattern={"type": "regex", "value": "x"},
        rationale="r",
        fixtures={"positive": [], "negative": []},
        scope={"file_patterns": ["*.md"]},
        status="stable",
        since="0.1.0",
    )
    assert rule.references == []
    assert rule.context_rules == {}
    assert rule.weight_override is None
    assert rule.default_active is True


def test_allowlist_entry_to_dict() -> None:
    e = AllowlistEntry(rule="R", path="docs/x.md", justification="j", expires=None)
    d = e.to_dict()
    assert d == {"rule": "R", "path": "docs/x.md", "justification": "j", "expires": None}


def test_tool_entry_to_dict() -> None:
    t = ToolEntry(name="cisco-ai-skill-scanner", version="2.0.9", mode="primary", sha="abc")
    d = t.to_dict()
    assert d["name"] == "cisco-ai-skill-scanner"
    assert d["sha"] == "abc"
    assert d["blocking"] is True


def test_policy_dataclass_defaults() -> None:
    p = Policy(name="x")
    assert p.version == 1
    assert p.required_scans == []
