"""PI-UNI-003 — Trojan Source bidi override (U+202A-U+202E, U+2066-U+2069)."""

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
        (rules_root / "unicode-tags" / "PI-UNI-003-bidi-override.yml")
        .read_text(encoding="utf-8")
    )
    assert_yaml_valid(raw, rule_v1_schema)


def test_bidi_override_matches(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("PI-UNI-003")
    text = "var x = '‮safe‬'; // attacker"
    expect_match(rule, text, file_path="skills/x/SKILL.md")


def test_no_bidi_does_not_match(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("PI-UNI-003")
    expect_no_match(rule, "var x = 'safe'; // attacker", file_path="skills/x/SKILL.md")


def test_isolate_codepoints_match(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("PI-UNI-003")
    expect_match(rule, "x ⁦ hidden ⁩ y", file_path="skills/x/SKILL.md")


def test_weight_override_locked(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("PI-UNI-003")
    assert rule.weight_override == 1.00
