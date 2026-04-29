"""Tests for the SPDX identifier list."""

from __future__ import annotations

from pruner_wrapper.spdx import is_valid_spdx


def test_common_identifiers_are_valid() -> None:
    assert is_valid_spdx("Apache-2.0")
    assert is_valid_spdx("MIT")
    assert is_valid_spdx("BSD-3-Clause")
    assert is_valid_spdx("GPL-3.0-only")


def test_invalid_strings_rejected() -> None:
    assert not is_valid_spdx("Apache 2")
    assert not is_valid_spdx("apache-2.0")
    assert not is_valid_spdx("MIT License")
    assert not is_valid_spdx("")
