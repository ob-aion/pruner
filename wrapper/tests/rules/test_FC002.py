"""FC002 — description length 1-1024."""

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
    rule_v1_schema: dict[str, Any],
    rules_root: Any,
) -> None:
    raw = yaml.safe_load(
        (rules_root / "frontmatter-conformance" / "FC002-description-length.yml")
        .read_text(encoding="utf-8")
    )
    assert_yaml_valid(raw, rule_v1_schema)


def test_short_description_passes(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("FC002")
    expect_no_match(rule, with_skill_frontmatter(description="Formats Python."))


def test_empty_description_fails(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("FC002")
    expect_match(rule, with_skill_frontmatter(description=""))


def test_oversized_description_fails(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("FC002")
    expect_match(rule, with_skill_frontmatter(description="x" * 1500))
