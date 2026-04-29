"""PI-UNI-001 — Unicode Tag block U+E0000-U+E007F."""

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
        (rules_root / "unicode-tags" / "PI-UNI-001-tag-block.yml").read_text(encoding="utf-8")
    )
    assert_yaml_valid(raw, rule_v1_schema)


def test_tag_block_payload_matches(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("PI-UNI-001")
    text = "Hello\U000E0049\U000E0067\U000E006E\U000E006F\U000E0072\U000E0065"
    expect_match(rule, text, file_path="skills/x/SKILL.md")


def test_pure_ascii_does_not_match(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("PI-UNI-001")
    expect_no_match(rule, "Plain ASCII content.", file_path="skills/x/SKILL.md")


def test_weight_override_locked(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("PI-UNI-001")
    assert rule.weight_override == 1.00
