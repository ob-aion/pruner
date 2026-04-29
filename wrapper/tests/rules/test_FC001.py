"""FC001 — name kebab-case + reserved-token check."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import yaml

from pruner_wrapper.types import Rule
from tests.rules._helpers import (
    assert_yaml_valid,
    expect_match,
    expect_no_match,
    with_skill_frontmatter,
)


def test_yaml_validates_against_schema(
    rule_loader: Callable[[str], Rule],
    rule_v1_schema: dict[str, Any],
    rules_root: Any,
) -> None:
    raw = yaml.safe_load((rules_root / "frontmatter-conformance" / "FC001-name-kebab-case.yml")
                         .read_text(encoding="utf-8"))
    assert_yaml_valid(raw, rule_v1_schema)


def test_kebab_case_passes(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("FC001")
    expect_no_match(rule, with_skill_frontmatter(name="code-formatter"))
    expect_no_match(rule, with_skill_frontmatter(name="format-py"))


def test_capitalised_name_fails(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("FC001")
    expect_match(rule, with_skill_frontmatter(name="Anthropic_Helper"))


def test_space_in_name_fails(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("FC001")
    expect_match(rule, with_skill_frontmatter(name="code formatter"))


def test_reserved_token_fails(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("FC001")
    expect_match(rule, with_skill_frontmatter(name="anthropic-helper"))


def test_claude_prefix_allowed(rule_loader: Callable[[str], Rule]) -> None:
    """`claude-md`, `claude-api` etc. reference Claude as a target agent,
    not as a publisher identity. Allowed."""
    rule = rule_loader("FC001")
    expect_no_match(rule, with_skill_frontmatter(name="claude-md"))
    expect_no_match(rule, with_skill_frontmatter(name="claude-api"))
