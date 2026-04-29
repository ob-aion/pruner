"""FC004 — metadata.version forbidden."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import yaml

from pruner_wrapper.types import Rule
from tests.rules._helpers import assert_yaml_valid, expect_match, expect_no_match

WITH_VERSION = """---
name: "x"
description: "y"
metadata:
  version: "1.0.0"
---
"""

WITHOUT_VERSION = """---
name: "x"
description: "y"
metadata:
  author: coroboros
---
"""


def test_yaml_validates_against_schema(
    rule_v1_schema: dict[str, Any], rules_root: Any
) -> None:
    raw = yaml.safe_load(
        (rules_root / "frontmatter-conformance" / "FC004-metadata-version-forbidden.yml")
        .read_text(encoding="utf-8")
    )
    assert_yaml_valid(raw, rule_v1_schema)


def test_clean_passes(rule_loader: Callable[[str], Rule]) -> None:
    expect_no_match(rule_loader("FC004"), WITHOUT_VERSION)


def test_metadata_version_present_fails(rule_loader: Callable[[str], Rule]) -> None:
    expect_match(rule_loader("FC004"), WITH_VERSION)
