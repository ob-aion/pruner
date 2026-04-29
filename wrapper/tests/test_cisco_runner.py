"""Tests for the Cisco runner subprocess wrapper."""

from __future__ import annotations

from pruner_wrapper.cisco_runner import (
    CISCO_BINARY,
    PINNED_VERSION,
    license_drift_check,
)


def test_pinned_version_constant() -> None:
    assert PINNED_VERSION == "2.0.9"


def test_binary_name_is_skill_scanner() -> None:
    assert CISCO_BINARY == "skill-scanner"


def test_license_drift_check_apache_marker() -> None:
    assert license_drift_check("Apache License\nVersion 2.0\n")
    assert license_drift_check("Licensed under Apache-2.0")
    assert license_drift_check("apache.org/licenses/LICENSE-2.0")


def test_license_drift_check_rejects_other() -> None:
    assert not license_drift_check("Mozilla Public License 2.0")
    assert not license_drift_check("")
    assert not license_drift_check("MIT License")
