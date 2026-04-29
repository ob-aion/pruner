"""Shared helpers for per-rule tests."""

from __future__ import annotations

from typing import Any

import jsonschema

from pruner_wrapper.pack_runner import scan_rule_against_text
from pruner_wrapper.types import Rule


def assert_yaml_valid(rule_dict: dict[str, Any], schema: dict[str, Any]) -> None:
    jsonschema.validate(instance=rule_dict, schema=schema)


def expect_match(rule: Rule, text: str, *, file_path: str = "skills/x/SKILL.md") -> None:
    """Assert the rule fires on `text`."""

    findings = scan_rule_against_text(rule, text, file_path=file_path)
    assert findings, f"expected rule {rule.id} to match: {text!r}"


def expect_no_match(rule: Rule, text: str, *, file_path: str = "skills/x/SKILL.md") -> None:
    """Assert the rule does NOT fire on `text`."""

    findings = scan_rule_against_text(rule, text, file_path=file_path)
    assert not findings, f"expected rule {rule.id} not to match {text!r}, got {findings}"


def with_skill_frontmatter(name: str = "code-formatter",
                           description: str = "Formats Python.",
                           extra: str = "") -> str:
    return f"""---
name: "{name}"
description: "{description}"
license: "Apache-2.0"
metadata:
  author: coroboros
{extra}
---
body
"""
