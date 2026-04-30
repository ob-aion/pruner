"""Pattern-type matchers for the Coroboros pack engine."""

from __future__ import annotations

from collections.abc import Callable

from pruner_wrapper.matchers.absence_regex_matcher import scan_absence_regex
from pruner_wrapper.matchers.codepoint_range_matcher import scan_codepoint_range
from pruner_wrapper.matchers.frontmatter_validator import scan_frontmatter
from pruner_wrapper.matchers.homoglyph_matcher import scan_homoglyph
from pruner_wrapper.matchers.pep723_validator import scan_pep723
from pruner_wrapper.matchers.regex_matcher import scan_regex
from pruner_wrapper.matchers.tool_grant_validator import scan_tool_grant
from pruner_wrapper.types import Finding, Rule

MatcherFn = Callable[[Rule, str, str], list[Finding]]
"""Signature: (rule, file_path, file_text) -> list[Finding]."""

MATCHERS: dict[str, MatcherFn] = {
    "regex": scan_regex,
    "absence-regex": scan_absence_regex,
    "codepoint-range": scan_codepoint_range,
    "homoglyph-instruction": scan_homoglyph,
    "frontmatter-validator": scan_frontmatter,
    "pep723-validator": scan_pep723,
    "tool-grant-validator": scan_tool_grant,
}


def dispatch(rule: Rule, file_path: str, file_text: str) -> list[Finding]:
    """Dispatch a rule to its matcher; raise on unknown pattern type."""

    pattern_type = rule.pattern.get("type")
    if pattern_type not in MATCHERS:
        raise ValueError(f"Unknown pattern type for rule {rule.id}: {pattern_type!r}")
    return MATCHERS[pattern_type](rule, file_path, file_text)


__all__ = [
    "MATCHERS",
    "MatcherFn",
    "dispatch",
    "scan_absence_regex",
    "scan_codepoint_range",
    "scan_frontmatter",
    "scan_homoglyph",
    "scan_pep723",
    "scan_regex",
    "scan_tool_grant",
]
