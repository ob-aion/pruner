"""Coroboros pack runner — load rules, walk the target tree, dispatch matchers."""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any

import yaml

from pruner_wrapper.matchers import dispatch
from pruner_wrapper.source_confidence import classify, weight_for
from pruner_wrapper.types import (
    SEVERITY_RANK,
    Category,
    Finding,
    Rule,
    Severity,
    SourceConfidence,
)

DEFAULT_PACK_DIR = Path("rules")


def load_rule(path: Path) -> Rule:
    """Load a single YAML rule file."""

    raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Rule file {path} did not parse to a mapping.")
    return _rule_from_dict(raw)


def _rule_from_dict(raw: dict[str, Any]) -> Rule:
    """Construct a `Rule` from a parsed YAML mapping. Validates required keys."""

    required = {"id", "slug", "title", "severity", "category", "pattern", "rationale", "fixtures",
                "scope", "status", "since"}
    missing = required - raw.keys()
    if missing:
        raise ValueError(f"Rule {raw.get('id', '<unknown>')} missing keys: {sorted(missing)}")
    return Rule(
        id=str(raw["id"]),
        slug=str(raw["slug"]),
        title=str(raw["title"]),
        severity=raw["severity"],
        category=raw["category"],
        pattern=dict(raw["pattern"]),
        rationale=str(raw["rationale"]),
        fixtures=dict(raw["fixtures"]),
        scope=dict(raw["scope"]),
        status=str(raw["status"]),
        since=str(raw["since"]),
        owasp_ref=raw.get("owasp_ref"),
        owasp_ast=raw.get("owasp_ast"),
        references=list(raw.get("references") or []),
        context_rules=dict(raw.get("context_rules") or {}),
        weight_override=raw.get("weight_override"),
        fix=raw.get("fix"),
        default_active=bool(raw.get("default_active", True)),
    )


def load_pack(rules_root: Path) -> list[Rule]:
    """Walk `rules_root` and load every YAML rule file found."""

    rules: list[Rule] = []
    if not rules_root.exists():
        return rules
    for path in sorted(rules_root.rglob("*.yml")):
        if path.name == "README.md":
            continue
        try:
            rules.append(load_rule(path))
        except (ValueError, yaml.YAMLError):
            continue
    return rules


def file_matches_scope(file_path: str, scope_patterns: list[str]) -> bool:
    """Return True if `file_path` matches any glob in `scope_patterns`."""

    return any(_glob(file_path, p) for p in scope_patterns)


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


def scan_rule_against_text(
    rule: Rule, file_text: str, *, file_path: str = "<inline>"
) -> list[Finding]:
    """Run a single rule against in-memory text. Used by tests."""

    return dispatch(rule, file_path, file_text)


def scan_tree(
    *,
    root: Path,
    rules: list[Rule],
    skill_pattern: str = "skills/*/SKILL.md",
    scan_prompt_defense: bool = False,
) -> list[Finding]:
    """Walk `root`, run every applicable rule against every applicable file.

    Matching protocol:
      1. Filter rules by `default_active` and `scan_prompt_defense` toggle.
      2. For each rule, walk `root` and collect files matching the rule's
         `scope.file_patterns`.
      3. Dispatch to the matcher; tag each finding with `source_confidence`
         and `severity_effective` (severity downgraded by source weight unless
         `weight_override` is set on the rule).
    """

    active_rules = [
        r
        for r in rules
        if r.default_active or (r.category == "prompt-defense" and scan_prompt_defense)
    ]
    if not active_rules:
        return []

    findings: list[Finding] = []
    file_cache: dict[Path, str] = {}

    for rule in active_rules:
        scope_patterns: list[str] = list(rule.scope.get("file_patterns") or [])
        if not scope_patterns:
            continue
        for absolute in _iter_files(root):
            relative = absolute.relative_to(root).as_posix()
            if not file_matches_scope(relative, scope_patterns):
                continue
            try:
                text = file_cache.setdefault(absolute, absolute.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError):
                continue
            for raw_finding in dispatch(rule, relative, text):
                tagged = _attach_source_confidence(raw_finding, rule)
                findings.append(tagged)
    return findings


def _iter_files(root: Path):  # type: ignore[no-untyped-def]
    """Yield every file under `root`, skipping common ignore dirs."""

    ignored_components = {".git", ".venv", "venv", "__pycache__", "node_modules",
                          ".mypy_cache", ".ruff_cache", ".pytest_cache"}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored_components for part in path.parts):
            continue
        yield path


def _attach_source_confidence(finding: Finding, rule: Rule) -> Finding:
    """Tag a finding with source-confidence + downgrade severity by weight."""

    sc: SourceConfidence = classify(finding.location.path)
    weight = weight_for(finding.location.path, override=rule.weight_override)
    finding.source_confidence = sc
    finding.severity_effective = _downgrade(finding.severity_declared, weight)
    return finding


def _downgrade(severity: Severity, weight: float) -> Severity:
    """Downgrade `severity` by `weight`. weight=1.0 keeps; weight=0.25 drops two ranks."""

    rank = SEVERITY_RANK[severity]
    if weight >= 0.99:
        return severity
    new_rank = max(0, rank - 1) if weight >= 0.4 else max(0, rank - 2)
    inverted = {v: k for k, v in SEVERITY_RANK.items()}
    return inverted[new_rank]


def filter_by_threshold(findings: list[Finding], threshold: Severity) -> list[Finding]:
    """Return only findings with `severity_effective` ≥ `threshold`."""

    cutoff = SEVERITY_RANK[threshold]
    return [f for f in findings if SEVERITY_RANK[f.severity_effective] >= cutoff]


__all__ = [
    "DEFAULT_PACK_DIR",
    "Category",
    "file_matches_scope",
    "filter_by_threshold",
    "load_pack",
    "load_rule",
    "scan_rule_against_text",
    "scan_tree",
]
