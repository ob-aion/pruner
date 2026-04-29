"""Tests for the codepoint-range matcher."""

from __future__ import annotations

from pruner_wrapper.matchers.codepoint_range_matcher import scan_codepoint_range
from pruner_wrapper.types import Rule


def _rule(*, ranges: list[list[str]], threshold: int = 1, **overrides: object) -> Rule:
    pat = {"type": "codepoint-range", "ranges": ranges}
    if threshold > 1:
        pat["threshold"] = threshold
    rule = Rule(
        id="X-UNI",
        slug="x",
        title="t",
        severity="critical",
        category="prompt-injection",
        pattern=pat,
        rationale="r",
        fixtures={"positive": [], "negative": []},
        scope={"file_patterns": ["**/*.md"]},
        status="stable",
        since="0.1.0",
    )
    for k, v in overrides.items():
        setattr(rule, k, v)
    return rule


def test_tag_block_match() -> None:
    rule = _rule(ranges=[["E0000", "E007F"]])
    text = "Hello\U000E0049\U000E0067\U000E006E\U000E006F"
    findings = scan_codepoint_range(rule, "skills/a/SKILL.md", text)
    assert len(findings) == 1
    assert findings[0].location.line == 1


def test_no_codepoints_in_range() -> None:
    rule = _rule(ranges=[["E0000", "E007F"]])
    assert scan_codepoint_range(rule, "a.md", "plain ASCII") == []


def test_threshold_below_does_not_fire() -> None:
    rule = _rule(ranges=[["FE00", "FE0F"]], threshold=4)
    # 2 variation selectors clustered → below threshold of 4
    assert scan_codepoint_range(rule, "a.md", "x︀︁y") == []


def test_threshold_at_fires() -> None:
    rule = _rule(ranges=[["FE00", "FE0F"]], threshold=4)
    # 4 variation selectors clustered → fires
    findings = scan_codepoint_range(rule, "a.md", "x︀︁︂︃y")
    assert len(findings) == 1


def test_invalid_range_skipped() -> None:
    rule = _rule(ranges=[["XX", "YY"]])
    assert scan_codepoint_range(rule, "a.md", "anything") == []


def test_multiple_clusters_each_emit() -> None:
    rule = _rule(ranges=[["FE00", "FE0F"]], threshold=2)
    text = "ab︀︁cd︂︃ef"
    findings = scan_codepoint_range(rule, "a.md", text)
    assert len(findings) == 2


def test_newline_breaks_cluster() -> None:
    rule = _rule(ranges=[["FE00", "FE0F"]], threshold=4)
    text = "︀︁\n︂︃"
    assert scan_codepoint_range(rule, "a.md", text) == []
