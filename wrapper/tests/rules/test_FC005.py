"""FC005 — license SPDX validation."""

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
    rule_v1_schema: dict[str, Any], rules_root: Any
) -> None:
    raw = yaml.safe_load(
        (rules_root / "frontmatter-conformance" / "FC005-license-spdx.yml")
        .read_text(encoding="utf-8")
    )
    assert_yaml_valid(raw, rule_v1_schema)


def test_apache_2_0_passes(rule_loader: Callable[[str], Rule]) -> None:
    expect_no_match(rule_loader("FC005"), with_skill_frontmatter())


def test_invalid_license_fails(rule_loader: Callable[[str], Rule]) -> None:
    text = """---
name: "x"
description: "y"
license: "Apache 2"
---
"""
    expect_match(rule_loader("FC005"), text)


def test_no_license_skipped_optional(rule_loader: Callable[[str], Rule]) -> None:
    text = """---
name: "x"
description: "y"
---
"""
    expect_no_match(rule_loader("FC005"), text)
