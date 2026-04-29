"""Compose findings into a single `report-v1.json` document.

Computes the per-category grade per PLAN §10:
  - Five buckets: secrets, permissions, injection, integrity, governance.
  - Each starts at 100; severity_points × source_confidence_weight is deducted.
  - Per-file cap of 10 deduction points per category per file for non-secret,
    non-PI-UNI findings on template/docs/test-fixture paths.
  - Score = round(mean(category_scores)). Bands: A>=90, B>=75, C>=60, D>=40, F<40.
"""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from pruner_wrapper import __version__
from pruner_wrapper.source_confidence import weight_for
from pruner_wrapper.types import (
    SEVERITY_DEDUCTION,
    AllowlistEntry,
    Category,
    Finding,
    ToolEntry,
)

CATEGORY_BUCKET: dict[Category, str] = {
    "prompt-injection": "injection",
    "prompt-defense": "injection",
    "secrets": "secrets",
    "permissions": "permissions",
    "integrity": "integrity",
    "supply-chain": "integrity",
    "governance": "governance",
}

BUCKETS: tuple[str, ...] = ("secrets", "permissions", "injection", "integrity", "governance")
PER_FILE_CAP = 10


def grade_band(score: int) -> str:
    """Band mapping per PLAN §10."""

    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def _is_capped(finding: Finding) -> bool:
    """Per-file cap applies to non-secret, non-PI-UNI findings on docs/template/test paths."""

    if finding.category == "secrets":
        return False
    if finding.id.startswith("PI-UNI-"):
        return False
    sc = finding.source_confidence
    return sc in {"template-example", "docs-example", "test-fixture"}


def compute_category_scores(findings: list[Finding]) -> dict[str, float]:
    """Compute score per bucket; per-file cap applied for downgraded paths."""

    scores: dict[str, float] = dict.fromkeys(BUCKETS, 100.0)
    per_file_deductions: dict[tuple[str, str], float] = defaultdict(float)

    for finding in findings:
        bucket = CATEGORY_BUCKET.get(finding.category, "integrity")
        deduction = SEVERITY_DEDUCTION[finding.severity_declared] * weight_for(
            finding.location.path,
            override=None,  # weight_override is already applied via severity_effective
        )
        # Use severity_effective deduction for the score (already source-weighted).
        deduction = float(SEVERITY_DEDUCTION[finding.severity_effective])

        if _is_capped(finding):
            key = (bucket, finding.location.path)
            allowed = max(0.0, PER_FILE_CAP - per_file_deductions[key])
            applied = min(deduction, allowed)
            per_file_deductions[key] += applied
        else:
            applied = deduction
        scores[bucket] = max(0.0, scores[bucket] - applied)
    return scores


def compute_overall_score(category_scores: dict[str, float]) -> int:
    """Mean across buckets, rounded."""

    if not category_scores:
        return 100
    return round(sum(category_scores.values()) / len(category_scores))


def by_severity_summary(findings: list[Finding]) -> dict[str, int]:
    counts: dict[str, int] = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        counts[f.severity_effective] += 1
    return counts


def by_source_confidence_summary(findings: list[Finding]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for f in findings:
        if f.source_confidence:
            counts[f.source_confidence] += 1
    return dict(counts)


def build_report(
    *,
    findings: list[Finding],
    allowlisted: list[AllowlistEntry],
    tools: list[ToolEntry],
    target_repo: str,
    target_commit: str | None,
    target_tag: str | None = None,
    target_path: str | None = None,
    policy_evaluation: dict[str, Any] | None = None,
    attestation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Render a `report-v1.json`-shaped dict."""

    category_scores = compute_category_scores(findings)
    score = compute_overall_score(category_scores)
    grade = grade_band(score)

    return {
        "schema_version": "1.0.0",
        "pruner_version": __version__,
        "scan_id": str(uuid.uuid4()),
        "target": {
            "repo": target_repo,
            "commit": target_commit,
            "tag": target_tag,
            "ref": None,
            "path": target_path,
        },
        "generated_at": datetime.now(tz=timezone.utc).isoformat(timespec="seconds"),
        "tools": [t.to_dict() for t in tools],
        "summary": {
            "total": len(findings),
            "by_severity": by_severity_summary(findings),
            "by_source_confidence": by_source_confidence_summary(findings),
            "by_category_score": {k: round(v, 1) for k, v in category_scores.items()},
            "score": score,
            "grade": grade,
        },
        "findings": [f.to_dict() for f in findings],
        "allowlisted": [a.to_dict() for a in allowlisted],
        "policy_evaluation": policy_evaluation
        or {"policy_name": "<none>", "policy_path": "", "compliant": True, "violations": []},
        "attestation": attestation or {},
    }
