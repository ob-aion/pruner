"""FC003 — custom fields must live under metadata."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import yaml

from pruner_wrapper.types import Rule
from tests.rules._helpers import assert_yaml_valid, expect_match, expect_no_match

SKILL_CLEAN = """---
name: "x"
description: "y"
metadata:
  custom_field: "value"
---
body
"""

SKILL_DIRTY = """---
name: "x"
description: "y"
custom_field: "value"
---
body
"""


def test_yaml_validates_against_schema(
    rule_v1_schema: dict[str, Any], rules_root: Any
) -> None:
    raw = yaml.safe_load(
        (rules_root / "frontmatter-conformance" / "FC003-custom-fields-under-metadata.yml")
        .read_text(encoding="utf-8")
    )
    assert_yaml_valid(raw, rule_v1_schema)


def test_clean_passes(rule_loader: Callable[[str], Rule]) -> None:
    expect_no_match(rule_loader("FC003"), SKILL_CLEAN)


def test_top_level_custom_field_fails(rule_loader: Callable[[str], Rule]) -> None:
    expect_match(rule_loader("FC003"), SKILL_DIRTY)
