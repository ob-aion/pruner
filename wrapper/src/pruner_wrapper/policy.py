"""Pruner org-policy evaluator — `.pruner-policy.yml`.

Failing policy fails the workflow regardless of `fail-on`.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any

import yaml

from pruner_wrapper.types import (
    SEVERITY_RANK,
    AllowlistEntry,
    Finding,
    Policy,
    Severity,
    ToolEntry,
)


class PolicyError(ValueError):
    """Raised on a malformed policy file."""


def load_policy(path: Path | None) -> Policy | None:
    """Load `.pruner-policy.yml`. Returns None if path is None or missing."""

    if path is None or not path.exists():
        return None
    raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise PolicyError(f"{path}: top-level must be a mapping")
    if raw.get("version") != 1:
        raise PolicyError(f"{path}: unknown policy version {raw.get('version')!r}")
    if not raw.get("name"):
        raise PolicyError(f"{path}: missing required field 'name'")
    return Policy(
        name=str(raw["name"]),
        version=int(raw["version"]),
        min_score=raw.get("min_score"),
        max_severity=raw.get("max_severity"),
        banned_rules_bypass=list(raw.get("banned_rules_bypass") or []),
        required_scans=list(raw.get("required_scans") or []),
        required_attestation=bool(raw.get("required_attestation", False)),
        scan_prompt_defense_posture=bool(raw.get("scan_prompt_defense_posture", False)),
        forbidden_paths=list(raw.get("forbidden_paths") or []),
    )


def evaluate(
    policy: Policy | None,
    *,
    findings: list[Finding],
    allowlisted: list[AllowlistEntry],
    tools: list[ToolEntry],
    score: int,
    target_paths: list[str],
) -> dict[str, Any]:
    """Apply `policy` against scan results. Returns the evaluation block."""

    if policy is None:
        return {
            "policy_name": "<none>",
            "policy_path": "",
            "compliant": True,
            "violations": [],
        }

    violations: list[dict[str, str]] = []

    if policy.min_score is not None and score < policy.min_score:
        violations.append(
            {"reason": "min_score", "detail": f"score {score} < min_score {policy.min_score}"}
        )

    if policy.max_severity is not None:
        cutoff = SEVERITY_RANK[policy.max_severity]
        for finding in findings:
            if SEVERITY_RANK[finding.severity_effective] > cutoff:
                violations.append(
                    {
                        "reason": "max_severity",
                        "detail": (
                            f"finding {finding.id} severity {finding.severity_effective} "
                            f"exceeds max_severity {policy.max_severity}"
                        ),
                    }
                )

    if policy.banned_rules_bypass:
        banned = set(policy.banned_rules_bypass)
        for entry in allowlisted:
            if entry.rule in banned:
                violations.append(
                    {
                        "reason": "banned_rules_bypass",
                        "detail": (
                            f"allowlist entry suppresses banned rule {entry.rule} "
                            f"at {entry.path}"
                        ),
                    }
                )

    if policy.required_scans:
        present = {tool.name for tool in tools}
        scan_to_tool = {
            "cisco": "cisco-ai-skill-scanner",
            "coroboros-pack": "pruner-wrapper",
            "gitleaks": "gitleaks",
            "actionlint": "actionlint",
            "snyk": "snyk-agent-scan",
        }
        for scan in policy.required_scans:
            expected = scan_to_tool.get(scan, scan)
            if expected not in present:
                violations.append(
                    {
                        "reason": "required_scans",
                        "detail": (
                            f"required scan {scan!r} not present "
                            f"(expected tool {expected!r})"
                        ),
                    }
                )

    if policy.forbidden_paths:
        for forbidden in policy.forbidden_paths:
            for path in target_paths:
                if fnmatch.fnmatch(path, forbidden):
                    violations.append(
                        {"reason": "forbidden_paths", "detail": f"forbidden path matched: {path}"}
                    )

    return {
        "policy_name": policy.name,
        "policy_path": ".pruner-policy.yml",
        "compliant": not violations,
        "violations": violations,
    }


def severity_satisfies(actual: Severity, threshold: Severity) -> bool:
    """Return True if `actual` is at or above `threshold` (rank-wise)."""

    return SEVERITY_RANK[actual] >= SEVERITY_RANK[threshold]
