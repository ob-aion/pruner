"""Tests for the badge SVG emitter — Coroboros Design Direction tokens."""

from __future__ import annotations

from pruner_wrapper.badge import GRADE_COLOR, render_badge_svg


def test_grade_a_uses_temporal_gold() -> None:
    svg = render_badge_svg(grade="A")
    assert GRADE_COLOR["A"] in svg
    assert "Grade A" in svg


def test_grade_f_uses_red() -> None:
    svg = render_badge_svg(grade="F")
    assert "#E53935" in svg


def test_no_gradient_no_shadow_no_rounded() -> None:
    svg = render_badge_svg(grade="B")
    forbidden = ("linearGradient", "radialGradient", "filter:", "filter=", "rx=\"", "ry=\"")
    for marker in forbidden:
        assert marker not in svg, f"badge SVG contains forbidden token {marker!r}"


def test_void_background() -> None:
    svg = render_badge_svg(grade="C")
    assert 'fill="#000000"' in svg


def test_jetbrains_mono_font() -> None:
    svg = render_badge_svg(grade="A")
    assert "JetBrains Mono" in svg


def test_engine_sha_appears_truncated() -> None:
    svg = render_badge_svg(grade="A", engine_sha="f2858cf3bc1be94e9a51ce0bca9c8d87c64364d7")
    assert "f2858cf3" in svg
    # The full long SHA should NOT appear in entirety (truncated to 8).
    assert "c64364d7" not in svg


def test_unknown_grade_falls_back_to_red() -> None:
    svg = render_badge_svg(grade="?")
    assert "#E53935" in svg
