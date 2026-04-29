"""SARIF 2.1.0 emit + parse — minimal subset Pruner uses."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from pruner_wrapper.types import Finding, Location, Severity

SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"
SARIF_VERSION = "2.1.0"

SEVERITY_TO_LEVEL: dict[Severity, str] = {
    "critical": "error",
    "high": "error",
    "medium": "warning",
    "low": "note",
    "info": "none",
}

LEVEL_TO_SEVERITY: dict[str, Severity] = {
    "error": "high",
    "warning": "medium",
    "note": "low",
    "none": "info",
}


def findings_to_sarif(
    findings: list[Finding],
    *,
    tool_name: str,
    tool_version: str,
    rules: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Render `findings` into a SARIF 2.1.0 document."""

    return {
        "$schema": SARIF_SCHEMA,
        "version": SARIF_VERSION,
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": tool_name,
                        "version": tool_version,
                        "informationUri": "https://github.com/ob-aion/pruner",
                        "rules": rules or [],
                    }
                },
                "results": [_finding_to_result(f) for f in findings],
            }
        ],
    }


def _finding_to_result(f: Finding) -> dict[str, Any]:
    region: dict[str, Any] = {}
    if f.location.line is not None:
        region["startLine"] = f.location.line
    if f.location.start_column is not None:
        region["startColumn"] = f.location.start_column
    if f.location.end_column is not None:
        region["endColumn"] = f.location.end_column

    physical: dict[str, Any] = {
        "artifactLocation": {"uri": f.location.path},
    }
    if region:
        physical["region"] = region

    result: dict[str, Any] = {
        "ruleId": f.id,
        "level": SEVERITY_TO_LEVEL[f.severity_effective],
        "message": {"text": f.message},
        "locations": [{"physicalLocation": physical}],
    }
    properties: dict[str, Any] = {
        "category": f.category,
        "severity_declared": f.severity_declared,
        "severity_effective": f.severity_effective,
    }
    if f.source_confidence:
        properties["source_confidence"] = f.source_confidence
    if f.owasp_ref:
        properties["owasp_ref"] = f.owasp_ref
    if f.owasp_ast:
        properties["owasp_ast"] = f.owasp_ast
    if f.evidence_snippet:
        properties["evidence_snippet"] = f.evidence_snippet
    if f.rationale_ref:
        properties["rationale_ref"] = f.rationale_ref
    if f.remediation:
        properties["remediation"] = f.remediation
    result["properties"] = properties
    return result


def findings_from_sarif(
    sarif: dict[str, Any], *, default_tool_name: str = "external"
) -> list[Finding]:
    """Parse a SARIF document into a list of `Finding`s."""

    out: list[Finding] = []
    for run in sarif.get("runs", []):
        tool = run.get("tool", {}).get("driver", {}).get("name", default_tool_name)
        for result in run.get("results", []):
            out.extend(_parse_result(result, tool_name=tool))
    return out


def _parse_result(result: dict[str, Any], *, tool_name: str) -> list[Finding]:
    rule_id = result.get("ruleId", "EXTERNAL")
    level = result.get("level", "warning")
    severity = LEVEL_TO_SEVERITY.get(level, "medium")
    properties = result.get("properties", {})
    severity_declared: Severity = properties.get("severity_declared", severity)
    severity_effective: Severity = properties.get("severity_effective", severity)
    category = properties.get("category", "integrity")
    text = result.get("message", {}).get("text", rule_id)

    findings: list[Finding] = []
    locations = result.get("locations") or [{}]
    for loc in locations:
        physical = loc.get("physicalLocation", {})
        artifact = physical.get("artifactLocation", {})
        region = physical.get("region", {})
        location = Location(
            path=artifact.get("uri", "<unknown>"),
            line=region.get("startLine"),
            start_column=region.get("startColumn"),
            end_column=region.get("endColumn"),
        )
        findings.append(
            Finding(
                id=rule_id,
                category=category,
                severity_declared=severity_declared,
                severity_effective=severity_effective,
                tool=tool_name,
                location=location,
                message=text,
                source_confidence=properties.get("source_confidence"),
                owasp_ref=properties.get("owasp_ref"),
                owasp_ast=properties.get("owasp_ast"),
                evidence_snippet=properties.get("evidence_snippet", ""),
                rationale_ref=properties.get("rationale_ref"),
                remediation=properties.get("remediation"),
            )
        )
    return findings


def write_sarif(findings: list[Finding], path: Path, *, tool_name: str, tool_version: str) -> None:
    """Serialise findings as SARIF and write to `path`."""

    path.parent.mkdir(parents=True, exist_ok=True)
    sarif = findings_to_sarif(findings, tool_name=tool_name, tool_version=tool_version)
    path.write_text(json.dumps(sarif, indent=2), encoding="utf-8")


def read_sarif(path: Path) -> dict[str, Any]:
    """Read and parse a SARIF document from `path`."""

    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))
