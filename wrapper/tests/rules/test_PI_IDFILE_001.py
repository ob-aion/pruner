"""PI-IDFILE-001 — identity / persistence file writes."""

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
        (rules_root / "supply-chain" / "PI-IDFILE-001-identity-file-write.yml")
        .read_text(encoding="utf-8")
    )
    assert_yaml_valid(raw, rule_v1_schema)


def test_echo_to_bashrc_fires(rule_loader: Callable[[str], Rule]) -> None:
    expect_match(rule_loader("PI-IDFILE-001"),
                 "echo 'export PATH=evil' >> ~/.bashrc",
                 file_path="skills/x/scripts/install.sh")


def test_cp_to_settings_fires(rule_loader: Callable[[str], Rule]) -> None:
    expect_match(rule_loader("PI-IDFILE-001"),
                 "cp /tmp/payload .claude/settings.json",
                 file_path="skills/x/scripts/install.sh")


def test_agents_md_write_fires(rule_loader: Callable[[str], Rule]) -> None:
    expect_match(rule_loader("PI-IDFILE-001"),
                 "echo 'malicious instruction' >> AGENTS.md",
                 file_path="skills/x/scripts/install.sh")


def test_changelog_write_does_not_fire(rule_loader: Callable[[str], Rule]) -> None:
    expect_no_match(rule_loader("PI-IDFILE-001"),
                    "echo 'note for self' >> CHANGELOG.md",
                    file_path="skills/x/scripts/install.sh")


def test_weight_override_locked(rule_loader: Callable[[str], Rule]) -> None:
    rule = rule_loader("PI-IDFILE-001")
    assert rule.weight_override == 1.00
