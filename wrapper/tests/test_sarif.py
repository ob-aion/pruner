"""Tests for the SARIF emit + parse module."""

from __future__ import annotations

from pathlib import Path

from pruner_wrapper.sarif import (
    SARIF_SCHEMA,
    SARIF_VERSION,
    findings_from_sarif,
    findings_to_sarif,
    read_sarif,
    write_sarif,
)
from pruner_wrapper.types import Finding, Location


def _sample() -> Finding:
    return Finding(
        id="X-001",
        category="prompt-injection",
        severity_declared="critical",
        severity_effective="critical",
        tool="pruner-wrapper",
        location=Location(path="a.md", line=2, start_column=3, end_column=6),
        message="hidden tag block",
        owasp_ref="LLM01",
        owasp_ast="AST01",
        evidence_snippet="snip",
        rationale_ref="https://example.com",
        remediation="strip the chars",
    )


def test_emit_shape() -> None:
    sarif = findings_to_sarif([_sample()], tool_name="pruner-wrapper", tool_version="0.1.2")
    assert sarif["$schema"] == SARIF_SCHEMA
    assert sarif["version"] == SARIF_VERSION
    assert sarif["runs"][0]["tool"]["driver"]["name"] == "pruner-wrapper"
    result = sarif["runs"][0]["results"][0]
    assert result["ruleId"] == "X-001"
    assert result["level"] == "error"
    assert result["properties"]["owasp_ast"] == "AST01"


def test_roundtrip_parse() -> None:
    sarif = findings_to_sarif([_sample()], tool_name="pruner-wrapper", tool_version="0.1.2")
    parsed = findings_from_sarif(sarif, default_tool_name="x")
    assert len(parsed) == 1
    assert parsed[0].id == "X-001"
    assert parsed[0].owasp_ast == "AST01"
    assert parsed[0].location.line == 2


def test_write_and_read(tmp_path: Path) -> None:
    out = tmp_path / "out.sarif"
    write_sarif([_sample()], out, tool_name="pruner-wrapper", tool_version="0.1.2")
    sarif = read_sarif(out)
    assert sarif["version"] == SARIF_VERSION


def test_empty_findings_emit_empty_results() -> None:
    sarif = findings_to_sarif([], tool_name="pruner-wrapper", tool_version="0.1.2")
    assert sarif["runs"][0]["results"] == []


def test_parse_external_sarif_assigns_default_severity() -> None:
    external = {
        "version": "2.1.0",
        "runs": [
            {
                "tool": {"driver": {"name": "external"}},
                "results": [
                    {
                        "ruleId": "EXT-1",
                        "level": "warning",
                        "message": {"text": "found"},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "x.md"},
                                    "region": {"startLine": 1},
                                }
                            }
                        ],
                    }
                ],
            }
        ],
    }
    parsed = findings_from_sarif(external)
    assert len(parsed) == 1
    assert parsed[0].severity_effective == "medium"
    assert parsed[0].tool == "external"
