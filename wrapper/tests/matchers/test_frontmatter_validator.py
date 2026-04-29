"""Tests for the frontmatter-validator matcher."""

from __future__ import annotations

from pruner_wrapper.matchers.frontmatter_validator import scan_frontmatter
from pruner_wrapper.types import Rule


def _rule(pattern: dict[str, object], **overrides: object) -> Rule:
    rule = Rule(
        id="FC-X",
        slug="x",
        title="t",
        severity="medium",
        category="governance",
        pattern={"type": "frontmatter-validator", **pattern},
        rationale="r",
        fixtures={"positive": [], "negative": []},
        scope={"file_patterns": ["skills/**/SKILL.md"]},
        status="stable",
        since="0.1.0",
    )
    for k, v in overrides.items():
        setattr(rule, k, v)
    return rule


SKILL_TEMPLATE = """---
name: "{name}"
description: "{description}"
license: "{license_}"
metadata:
  author: coroboros
---
body
"""


def _skill(name: str = "code-formatter", description: str = "Formats Python.",
           license_: str = "Apache-2.0") -> str:
    return SKILL_TEMPLATE.format(name=name, description=description, license_=license_)


def test_must_match_pass() -> None:
    rule = _rule({"field": "name", "must_match": r"^[a-z][a-z0-9-]*$"})
    assert scan_frontmatter(rule, "skills/a/SKILL.md", _skill()) == []


def test_must_match_fail() -> None:
    rule = _rule({"field": "name", "must_match": r"^[a-z][a-z0-9-]*$"})
    findings = scan_frontmatter(rule, "skills/a/SKILL.md", _skill(name="Bad Name"))
    assert len(findings) == 1


def test_max_length_fail() -> None:
    rule = _rule({"field": "description", "max_length": 10})
    findings = scan_frontmatter(rule, "skills/a/SKILL.md", _skill(description="x" * 50))
    assert len(findings) == 1


def test_min_length_fail() -> None:
    rule = _rule({"field": "description", "min_length": 5})
    findings = scan_frontmatter(rule, "skills/a/SKILL.md", _skill(description=""))
    assert len(findings) == 1


def test_forbid_tokens_in_field() -> None:
    rule = _rule({"field": "name", "forbid_tokens": ["anthropic", "claude"]})
    findings = scan_frontmatter(rule, "skills/a/SKILL.md", _skill(name="claude-helper"))
    assert len(findings) == 1


def test_must_match_spdx_pass() -> None:
    rule = _rule({"field": "license", "must_match_spdx": True, "optional": True})
    assert scan_frontmatter(rule, "skills/a/SKILL.md", _skill(license_="Apache-2.0")) == []


def test_must_match_spdx_fail() -> None:
    rule = _rule({"field": "license", "must_match_spdx": True, "optional": True})
    findings = scan_frontmatter(rule, "skills/a/SKILL.md", _skill(license_="Apache 2"))
    assert len(findings) == 1


def test_field_path_must_be_absent_pass() -> None:
    rule = _rule({"field_path": "metadata.version", "must_be_absent": True})
    assert scan_frontmatter(rule, "skills/a/SKILL.md", _skill()) == []


def test_field_path_must_be_absent_fail() -> None:
    rule = _rule({"field_path": "metadata.version", "must_be_absent": True})
    text = """---
name: "x"
description: "y"
metadata:
  version: "1.0"
---
"""
    findings = scan_frontmatter(rule, "skills/a/SKILL.md", text)
    assert len(findings) == 1


def test_forbid_top_level_fields_outside() -> None:
    rule = _rule({
        "forbid_top_level_fields_outside": [
            "name", "description", "allowed-tools", "disable-model-invocation",
            "license", "version", "metadata"
        ]
    })
    text = """---
name: "x"
description: "y"
custom_field: "bar"
---
"""
    findings = scan_frontmatter(rule, "skills/a/SKILL.md", text)
    assert len(findings) == 1
    assert "custom_field" in findings[0].message


def test_missing_frontmatter_optional() -> None:
    rule = _rule({"field": "license", "optional": True})
    assert scan_frontmatter(rule, "skills/a/SKILL.md", "no frontmatter here") == []


def test_missing_frontmatter_not_optional() -> None:
    rule = _rule({"field": "name"})
    findings = scan_frontmatter(rule, "skills/a/SKILL.md", "no frontmatter here")
    assert len(findings) == 1


def test_malformed_frontmatter_yaml() -> None:
    rule = _rule({"field": "name"})
    text = "---\nname: \"x\nbadly: quoted\n---\n"
    findings = scan_frontmatter(rule, "skills/a/SKILL.md", text)
    assert len(findings) == 1
