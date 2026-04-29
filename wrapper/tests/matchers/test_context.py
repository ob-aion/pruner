"""Tests for the shared context-rule helpers."""

from __future__ import annotations

from pruner_wrapper.matchers._context import (
    context_skip,
    fenced_block_lang_for_line,
    line_for_offset,
    line_starts_with_any,
    path_matches_any,
)


def test_path_matches_any_glob() -> None:
    assert path_matches_any("docs/x.md", ["docs/*"])
    assert path_matches_any("docs/sub/x.md", ["docs/**"])
    assert not path_matches_any("src/x.py", ["docs/**"])


def test_line_starts_with_any() -> None:
    assert line_starts_with_any("# comment", ["#"])
    assert line_starts_with_any("    // comment", ["//"])
    assert not line_starts_with_any("code", ["#"])


def test_line_for_offset() -> None:
    text = "line one\nline two\nline three"
    assert line_for_offset(text, 0) == (1, 1)
    assert line_for_offset(text, 9) == (2, 1)
    assert line_for_offset(text, 18) == (3, 1)


def test_fenced_block_lang_inside() -> None:
    text = "```python\nx = 1\ny = 2\n```\n"
    assert fenced_block_lang_for_line(text, 1) is None  # the ``` line itself
    assert fenced_block_lang_for_line(text, 2) == "python"
    assert fenced_block_lang_for_line(text, 5) is None


def test_fenced_block_lang_outside() -> None:
    text = "no fences here\n"
    assert fenced_block_lang_for_line(text, 1) is None


def test_context_skip_path() -> None:
    assert context_skip(
        {"skip_if_path_matches": ["docs/**"]}, path="docs/x.md", line_text="anything"
    )


def test_context_skip_line_prefix() -> None:
    assert context_skip(
        {"skip_if_line_starts_with": ["#"]},
        path="src/x.py",
        line_text="# comment",
    )


def test_context_skip_fenced_lang() -> None:
    assert context_skip(
        {"skip_if_fenced_block_lang_in": ["example"]},
        path="docs/x.md",
        fenced_lang="example",
    )


def test_context_skip_no_rules() -> None:
    assert not context_skip({}, path="x.md")
