"""Tests for the lore message catalog."""

from __future__ import annotations

from pruner_wrapper import lore


def test_known_key_formats() -> None:
    assert lore.message("scan_start", threshold="critical").startswith("Pruning")


def test_unknown_key_returns_input() -> None:
    assert lore.message("does-not-exist") == "does-not-exist"


def test_missing_format_arg_falls_back() -> None:
    # Missing field — return the unformatted template rather than raising.
    out = lore.message("scan_start")
    assert "{threshold}" in out


def test_lore_strings_are_ascii_safe() -> None:
    for value in lore.LORE.values():
        assert value.isascii(), f"non-ASCII lore string: {value!r}"
