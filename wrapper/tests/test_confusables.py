"""Tests for the confusables table + has_any_homoglyph helper."""

from __future__ import annotations

from pruner_wrapper.confusables import (
    ASCII_TO_CONFUSABLES,
    confusables_for,
    has_any_homoglyph,
)


def test_table_covers_target_token_chars() -> None:
    needed = set("ignoresystempromptinstructionsoverridedisregardforget"
                 "youarenowadminroot")
    needed.discard(" ")
    missing = needed - ASCII_TO_CONFUSABLES.keys()
    assert not missing, f"missing confusables for: {sorted(missing)}"


def test_confusables_for_unknown_returns_empty() -> None:
    assert confusables_for("?") == frozenset()


def test_has_any_homoglyph_pure_ascii_false() -> None:
    assert not has_any_homoglyph("ignore", "ignore")


def test_has_any_homoglyph_cyrillic_o() -> None:
    # 'ignоre' with Cyrillic о (U+043E)
    assert has_any_homoglyph("ignоre", "ignore")


def test_has_any_homoglyph_length_mismatch() -> None:
    assert not has_any_homoglyph("ignor", "ignore")


def test_has_any_homoglyph_unrelated_chars() -> None:
    assert not has_any_homoglyph("xgnore", "ignore")
