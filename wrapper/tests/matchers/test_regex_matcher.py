"""Tests for the regex matcher."""

from __future__ import annotations

from pruner_wrapper.matchers.regex_matcher import scan_regex
from pruner_wrapper.types import Rule


def _rule(value: str, **overrides: object) -> Rule:
    base = Rule(
        id="X-1",
        slug="x",
        title="t",
        severity="high",
        category="prompt-injection",
        pattern={"type": "regex", "value": value},
        rationale="r",
        fixtures={"positive": [], "negative": []},
        scope={"file_patterns": ["**/*.md"]},
        status="stable",
        since="0.1.0",
    )
    for k, v in overrides.items():
        setattr(base, k, v)
    return base


def test_match_emits_finding() -> None:
    rule = _rule(r"badword")
    findings = scan_regex(rule, "skills/a/SKILL.md", "ok line\nthis has badword here\n")
    assert len(findings) == 1
    assert findings[0].location.line == 2


def test_no_match_emits_nothing() -> None:
    rule = _rule(r"absent")
    assert scan_regex(rule, "a.md", "totally clean") == []


def test_invalid_regex_returns_empty() -> None:
    rule = _rule(r"(")  # invalid
    assert scan_regex(rule, "a.md", "anything") == []


def test_empty_pattern_returns_empty() -> None:
    rule = _rule("")
    assert scan_regex(rule, "a.md", "anything") == []


def test_one_finding_per_line() -> None:
    rule = _rule(r"x")
    findings = scan_regex(rule, "a.md", "x x x\nx x x\n")
    # One per line max, even with multiple regex hits per line.
    assert len(findings) == 2


def test_context_skip_path_suppresses() -> None:
    rule = _rule(r"hit")
    rule.context_rules = {"skip_if_path_matches": ["docs/**"]}
    assert scan_regex(rule, "docs/x.md", "this is a hit") == []


def test_context_skip_line_starts_with() -> None:
    rule = _rule(r"hit")
    rule.context_rules = {"skip_if_line_starts_with": ["#"]}
    findings = scan_regex(rule, "x.md", "# hit\nreal hit\n")
    assert len(findings) == 1
    assert findings[0].location.line == 2


def test_ignore_in_fenced_blocks() -> None:
    rule = _rule(r"hit")
    rule.scope = {"file_patterns": ["**/*.md"], "ignore_in_fenced_blocks": True}
    text = "```\nhit\n```\nclean\n"
    findings = scan_regex(rule, "x.md", text)
    # The "hit" inside the fenced block should be suppressed.
    assert all(f.location.line != 2 for f in findings)
