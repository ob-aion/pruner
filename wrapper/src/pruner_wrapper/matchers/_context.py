"""Shared helpers for context-rule FP suppression and fenced-block detection."""

from __future__ import annotations

import fnmatch
import re
from typing import Any

FENCED_BLOCK_RE = re.compile(r"^(```|~~~)\s*([A-Za-z0-9_+-]*)\s*$")


def path_matches_any(path: str, patterns: list[str]) -> bool:
    """Glob-match `path` against any of `patterns`."""

    return any(_glob(path, p) for p in patterns)


def _glob(path: str, pattern: str) -> bool:
    if "**" not in pattern:
        return fnmatch.fnmatch(path, pattern)
    return _segment_match(path.split("/"), pattern.split("/"))


def _segment_match(path_parts: list[str], pattern_parts: list[str]) -> bool:
    if not pattern_parts:
        return not path_parts
    head, *tail = pattern_parts
    if head == "**":
        if not tail:
            return True
        return any(_segment_match(path_parts[i:], tail) for i in range(len(path_parts) + 1))
    if not path_parts:
        return False
    if fnmatch.fnmatch(path_parts[0], head):
        return _segment_match(path_parts[1:], tail)
    return False


def line_starts_with_any(line: str, prefixes: list[str]) -> bool:
    """Return True if `line` (after lstrip) starts with any of `prefixes`."""

    stripped = line.lstrip()
    return any(stripped.startswith(p) for p in prefixes)


def fenced_block_lang_for_line(text: str, line_num: int) -> str | None:
    """Return the fenced-block language for `line_num` (1-indexed), or None.

    A line is "inside" a fenced block if there is an opening fence above it
    (with no matching closing fence between the fence and the line). Returns
    the language tag of the enclosing fence, or `None` if the line is not in
    a fenced block.
    """

    if line_num < 1:
        return None

    lines = text.splitlines()
    if line_num > len(lines):
        return None

    in_fence = False
    fence_lang: str | None = None

    for i, raw in enumerate(lines, start=1):
        match = FENCED_BLOCK_RE.match(raw)
        if i == line_num:
            return fence_lang if in_fence else None
        if match:
            if in_fence:
                in_fence = False
                fence_lang = None
            else:
                in_fence = True
                fence_lang = match.group(2) or ""
    return None


def line_for_offset(text: str, offset: int) -> tuple[int, int]:
    """Return (line_number, column) (both 1-indexed) for byte offset `offset`."""

    if offset <= 0:
        return 1, 1
    head = text[:offset]
    line_num = head.count("\n") + 1
    last_newline = head.rfind("\n")
    column = offset - last_newline if last_newline >= 0 else offset + 1
    return line_num, column


def _str_list(value: object) -> list[str]:
    """Coerce an unknown YAML field into a list[str]."""

    if not value:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    return []


def context_skip(
    rule_context_rules: dict[str, Any],
    *,
    path: str,
    line_text: str | None = None,
    fenced_lang: str | None = None,
) -> bool:
    """Return True if a finding at this location should be suppressed."""

    if not rule_context_rules:
        return False

    skip_path = _str_list(rule_context_rules.get("skip_if_path_matches"))
    if skip_path and path_matches_any(path, skip_path):
        return True

    skip_prefix = _str_list(rule_context_rules.get("skip_if_line_starts_with"))
    if line_text is not None and skip_prefix and line_starts_with_any(line_text, skip_prefix):
        return True

    skip_lang = _str_list(rule_context_rules.get("skip_if_fenced_block_lang_in"))
    return bool(fenced_lang is not None and skip_lang and fenced_lang in skip_lang)
