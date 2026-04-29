"""Tests for the compose / grade-band logic."""

from __future__ import annotations

from pruner_wrapper.compose import (
    BUCKETS,
    PER_FILE_CAP,
    build_report,
    by_severity_summary,
    by_source_confidence_summary,
    compute_category_scores,
    compute_overall_score,
    grade_band,
)
from pruner_wrapper.types import Finding, Location, ToolEntry


def _f(
    *,
    severity: str,
    category: str = "prompt-injection",
    path: str = "skills/a/SKILL.md",
    rule_id: str = "X-1",
) -> Finding:
    return Finding(
        id=rule_id,
        category=category,  # type: ignore[arg-type]
        severity_declared=severity,  # type: ignore[arg-type]
        severity_effective=severity,  # type: ignore[arg-type]
        tool="pruner-wrapper",
        location=Location(path=path, line=1, start_column=1, end_column=2),
        message="m",
        source_confidence="active-runtime",
    )


def test_grade_band_thresholds() -> None:
    assert grade_band(100) == "A"
    assert grade_band(90) == "A"
    assert grade_band(89) == "B"
    assert grade_band(75) == "B"
    assert grade_band(60) == "C"
    assert grade_band(40) == "D"
    assert grade_band(39) == "F"


def test_buckets_are_five() -> None:
    assert len(BUCKETS) == 5


def test_compute_scores_clean() -> None:
    scores = compute_category_scores([])
    for bucket in BUCKETS:
        assert scores[bucket] == 100.0


def test_compute_scores_critical_finding() -> None:
    scores = compute_category_scores([_f(severity="critical")])
    assert scores["injection"] == 75.0


def test_compute_scores_per_file_cap_for_template_paths() -> None:
    """Template-path findings cap at PER_FILE_CAP per category per file."""

    f = _f(severity="critical")
    f.location = Location(path="examples/x.md")
    f.source_confidence = "template-example"
    findings = [f, f, f]   # 3 critical findings on same template path
    scores = compute_category_scores(findings)
    assert scores["injection"] == 100.0 - PER_FILE_CAP


def test_compute_scores_pi_uni_never_capped() -> None:
    f = _f(severity="critical", rule_id="PI-UNI-001")
    f.location = Location(path="docs/x.md")
    f.source_confidence = "docs-example"
    scores = compute_category_scores([f, f, f])
    assert scores["injection"] == 100.0 - 75.0  # 3 × 25 deduction, no cap


def test_compute_scores_secrets_never_capped() -> None:
    f = _f(severity="critical", category="secrets")
    f.location = Location(path="docs/x.md")
    f.source_confidence = "docs-example"
    scores = compute_category_scores([f, f, f])
    assert scores["secrets"] == 100.0 - 75.0


def test_overall_score_average() -> None:
    scores = dict.fromkeys(BUCKETS, 80.0)
    assert compute_overall_score(scores) == 80


def test_summary_helpers() -> None:
    findings = [
        _f(severity="critical"),
        _f(severity="high"),
        _f(severity="high"),
    ]
    sev = by_severity_summary(findings)
    assert sev["critical"] == 1
    assert sev["high"] == 2

    sc = by_source_confidence_summary(findings)
    assert sc["active-runtime"] == 3


def test_build_report_shape() -> None:
    report = build_report(
        findings=[_f(severity="medium")],
        allowlisted=[],
        tools=[ToolEntry(name="pruner-wrapper", version="0.1.3", mode="policy-pack")],
        target_repo="<test>",
        target_commit=None,
    )
    assert report["schema_version"] == "1.0.0"
    assert report["pruner_version"] == "0.1.3"
    assert report["summary"]["total"] == 1
    assert report["summary"]["grade"] in {"A", "B", "C", "D", "F"}
    assert "scan_id" in report
    assert "generated_at" in report
