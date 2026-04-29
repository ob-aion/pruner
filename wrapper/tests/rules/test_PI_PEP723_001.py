"""PI-PEP723-001 — inline-script deps without == pin."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import yaml

from pruner_wrapper.types import Rule
from tests.rules._helpers import assert_yaml_valid, expect_match, expect_no_match


PINNED = """# /// script
# dependencies = ["requests==2.31.0"]
# ///

import requests
"""

UNPINNED = """# /// script
# dependencies = ["requests"]
# ///

import requests
"""


def test_yaml_validates_against_schema(
    rule_v1_schema: dict[str, Any], rules_root: Any
) -> None:
    raw = yaml.safe_load(
        (rules_root / "supply-chain" / "PI-PEP723-001-inline-deps-unpinned.yml")
        .read_text(encoding="utf-8")
    )
    assert_yaml_valid(raw, rule_v1_schema)


def test_pinned_passes(rule_loader: Callable[[str], Rule]) -> None:
    expect_no_match(rule_loader("PI-PEP723-001"), PINNED, file_path="skills/x/scripts/a.py")


def test_unpinned_fires(rule_loader: Callable[[str], Rule]) -> None:
    expect_match(rule_loader("PI-PEP723-001"), UNPINNED, file_path="skills/x/scripts/a.py")
