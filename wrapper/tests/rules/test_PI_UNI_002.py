"""PI-UNI-002 — variation-selector clusters of >=4."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import yaml

from pruner_wrapper.types import Rule
from tests.rules._helpers import assert_yaml_valid, expect_match, expect_no_match


def test_yaml_validates_against_schema(
    rule_v1_schema: dict[str, Any], rules_root: Any
) -> None:
    raw = yaml.safe_load(
        (rules_root / "unicode-tags" / "PI-UNI-002-variation-selectors.yml")
        .read_text(encoding="utf-8")
    )
    assert_yaml_valid(raw, rule_v1_schema)


def test_cluster_of_four_matches(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("PI-UNI-002")
    expect_match(rule, "ascii︀︁︂︃ payload",
                 file_path="skills/x/SKILL.md")


def test_single_emoji_modifier_does_not_match(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("PI-UNI-002")
    # A single variation selector after an emoji is legitimate.
    expect_no_match(rule, "thumbs \U0001F44D️ up", file_path="skills/x/SKILL.md")


def test_weight_override_locked(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("PI-UNI-002")
    assert rule.weight_override == 1.00


def test_threshold_is_four(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("PI-UNI-002")
    assert rule.pattern["threshold"] == 4
