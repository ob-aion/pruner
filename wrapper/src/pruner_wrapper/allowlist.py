"""Pruner allowlist — `.pruner-ignore.yml` parser with mandatory justification."""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any

import yaml

from pruner_wrapper.types import AllowlistEntry, Finding


class AllowlistError(ValueError):
    """Raised on a malformed allowlist (missing justification, etc.)."""


def load_allowlist(path: Path | None) -> list[AllowlistEntry]:
    """Load an allowlist file. Returns empty list if `path` is None or missing."""

    if path is None or not path.exists():
        return []
    raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw is None:
        return []
    if not isinstance(raw, dict):
        raise AllowlistError(f"{path}: top-level must be a mapping")
    if raw.get("version") != 1:
        raise AllowlistError(f"{path}: unknown allowlist version {raw.get('version')!r}")

    entries: list[AllowlistEntry] = []
    for i, ignore in enumerate(raw.get("ignores") or []):
        if not isinstance(ignore, dict):
            raise AllowlistError(f"{path}: ignores[{i}] must be a mapping")
        for required in ("rule", "path", "justification"):
            if required not in ignore or not str(ignore[required]).strip():
                raise AllowlistError(
                    f"{path}: ignores[{i}] missing or empty {required!r}"
                )
        entries.append(
            AllowlistEntry(
                rule=str(ignore["rule"]),
                path=str(ignore["path"]),
                justification=str(ignore["justification"]),
                expires=(str(ignore["expires"]) if ignore.get("expires") else None),
            )
        )
    return entries


def apply_allowlist(
    findings: list[Finding], allowlist: list[AllowlistEntry]
) -> tuple[list[Finding], list[AllowlistEntry]]:
    """Suppress findings matched by the allowlist. Returns (kept, applied_entries)."""

    if not allowlist:
        return findings, []

    kept: list[Finding] = []
    applied: dict[tuple[str, str, str], AllowlistEntry] = {}
    for finding in findings:
        suppressed = False
        for entry in allowlist:
            if entry.rule != finding.id:
                continue
            if not _path_matches(finding.location.path, entry.path):
                continue
            applied[(entry.rule, entry.path, entry.justification)] = entry
            suppressed = True
            break
        if not suppressed:
            kept.append(finding)
    return kept, list(applied.values())


def _path_matches(path: str, pattern: str) -> bool:
    """Glob match — supports `**` for recursive subtrees."""

    if "**" not in pattern:
        return fnmatch.fnmatch(path, pattern) or path == pattern
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
