"""Core dataclasses shared across the wrapper modules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Severity = Literal["critical", "high", "medium", "low", "info"]
Category = Literal[
    "prompt-injection",
    "prompt-defense",
    "secrets",
    "permissions",
    "integrity",
    "governance",
    "supply-chain",
]
SourceConfidence = Literal[
    "active-runtime",
    "hook-code",
    "project-local-optional",
    "plugin-manifest",
    "template-example",
    "docs-example",
    "test-fixture",
]
ToolMode = Literal[
    "primary",
    "secrets",
    "policy-pack",
    "second-opinion",
    "posture",
    "workflow-lint",
]


SOURCE_CONFIDENCE_WEIGHT: dict[SourceConfidence, float] = {
    "active-runtime": 1.00,
    "hook-code": 1.00,
    "project-local-optional": 0.75,
    "plugin-manifest": 0.50,
    "template-example": 0.25,
    "docs-example": 0.25,
    "test-fixture": 0.25,
}

SEVERITY_DEDUCTION: dict[Severity, int] = {
    "critical": 25,
    "high": 15,
    "medium": 5,
    "low": 2,
    "info": 0,
}

SEVERITY_RANK: dict[Severity, int] = {
    "info": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


@dataclass
class Location:
    """A finding location in the audited tree."""

    path: str
    line: int | None = None
    start_column: int | None = None
    end_column: int | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"path": self.path}
        if self.line is not None:
            out["line"] = self.line
        if self.start_column is not None:
            out["start_column"] = self.start_column
        if self.end_column is not None:
            out["end_column"] = self.end_column
        return out


@dataclass
class Finding:
    """A single rule finding (Coroboros pack or external SARIF)."""

    id: str
    category: Category
    severity_declared: Severity
    severity_effective: Severity
    tool: str
    location: Location
    message: str
    source_confidence: SourceConfidence | None = None
    owasp_ref: str | None = None
    owasp_ast: str | None = None
    evidence_snippet: str = ""
    rationale_ref: str | None = None
    remediation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "severity_declared": self.severity_declared,
            "severity_effective": self.severity_effective,
            "source_confidence": self.source_confidence,
            "owasp_ref": self.owasp_ref,
            "owasp_ast": self.owasp_ast,
            "tool": self.tool,
            "location": self.location.to_dict(),
            "message": self.message,
            "evidence_snippet": self.evidence_snippet,
            "rationale_ref": self.rationale_ref,
            "remediation": self.remediation,
        }


@dataclass
class Rule:
    """A loaded Coroboros pack rule."""

    id: str
    slug: str
    title: str
    severity: Severity
    category: Category
    pattern: dict[str, Any]
    rationale: str
    fixtures: dict[str, Any]
    scope: dict[str, Any]
    status: str
    since: str
    owasp_ref: str | None = None
    owasp_ast: str | None = None
    references: list[str] = field(default_factory=list)
    context_rules: dict[str, Any] = field(default_factory=dict)
    weight_override: float | None = None
    fix: dict[str, Any] | None = None
    default_active: bool = True


@dataclass
class AllowlistEntry:
    """A single justification-mandatory allowlist entry."""

    rule: str
    path: str
    justification: str
    expires: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule": self.rule,
            "path": self.path,
            "justification": self.justification,
            "expires": self.expires,
        }


@dataclass
class Policy:
    """An org-level policy."""

    name: str
    version: int = 1
    min_score: int | None = None
    max_severity: Severity | None = None
    banned_rules_bypass: list[str] = field(default_factory=list)
    required_scans: list[str] = field(default_factory=list)
    required_attestation: bool = False
    scan_prompt_defense_posture: bool = False
    forbidden_paths: list[str] = field(default_factory=list)


@dataclass
class ToolEntry:
    """A tool that contributed to a report."""

    name: str
    version: str
    mode: ToolMode
    sha: str | None = None
    blocking: bool = True

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "name": self.name,
            "version": self.version,
            "mode": self.mode,
            "blocking": self.blocking,
        }
        if self.sha is not None:
            out["sha"] = self.sha
        return out
