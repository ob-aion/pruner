"""PI-UNI-005 — clustered zero-width characters."""

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
        (rules_root / "unicode-tags" / "PI-UNI-005-zero-width.yml").read_text(encoding="utf-8")
    )
    assert_yaml_valid(raw, rule_v1_schema)


def test_clustered_zwsp_fires(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("PI-UNI-005")
    text = "Hello​​​​ world"
    expect_match(rule, text, file_path="skills/x/SKILL.md")


def test_clustered_zwj_fires(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("PI-UNI-005")
    text = "secret‍‍‍‍ payload"
    expect_match(rule, text, file_path="skills/x/SKILL.md")


def test_bom_cluster_fires(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("PI-UNI-005")
    text = "x﻿﻿﻿﻿ y"
    expect_match(rule, text, file_path="skills/x/SKILL.md")


def test_single_zwj_does_not_fire(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("PI-UNI-005")
    expect_no_match(rule, "family‍ emoji", file_path="skills/x/SKILL.md")


def test_pure_ascii_does_not_fire(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("PI-UNI-005")
    expect_no_match(rule, "Plain ASCII content.", file_path="skills/x/SKILL.md")


def test_weight_override_locked(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("PI-UNI-005")
    assert rule.weight_override == 1.00
