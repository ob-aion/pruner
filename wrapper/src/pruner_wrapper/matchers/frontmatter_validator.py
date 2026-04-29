"""Frontmatter validator — `pattern.type: frontmatter-validator`.

Used by FC001-FC005. Parses the YAML frontmatter pre-amble (between leading
`---` lines) and applies one of:
  - `field` + `must_match` (regex)
  - `field` + `min_length` / `max_length`
  - `field` + `forbid_tokens` (case-insensitive)
  - `field` + `must_match_spdx`
  - `field_path` + `must_be_absent` (dotted path, e.g. `metadata.version`)
  - `forbid_top_level_fields_outside` (whitelisted top-level keys)
"""

from __future__ import annotations

import re
from typing import Any

import yaml

from pruner_wrapper.spdx import is_valid_spdx
from pruner_wrapper.types import Finding, Location, Rule


def _split_frontmatter(text: str) -> tuple[str | None, int]:
    """Return (frontmatter_yaml, frontmatter_line_count) or (None, 0)."""

    if not text.startswith("---"):
        return None, 0
    rest = text[3:]
    if rest.startswith("\n"):
        rest = rest[1:]
        line_offset = 1
    else:
        line_offset = 0
    end = rest.find("\n---")
    if end == -1:
        return None, 0
    body = rest[:end]
    return body, body.count("\n") + 1 + line_offset


def _resolve_path(data: dict[str, Any], dotted: str) -> tuple[bool, Any]:
    """Walk a dotted path; return (found, value)."""

    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return False, None
        cur = cur[part]
    return True, cur


def _emit(rule: Rule, file_path: str, message: str, line: int = 1) -> Finding:
    return Finding(
        id=rule.id,
        category=rule.category,
        severity_declared=rule.severity,
        severity_effective=rule.severity,
        tool="pruner-wrapper",
        location=Location(path=file_path, line=line, start_column=1, end_column=1),
        message=f"{rule.title} — {message}",
        owasp_ref=rule.owasp_ref,
        owasp_ast=rule.owasp_ast,
        evidence_snippet="",
        rationale_ref=rule.references[0] if rule.references else None,
        remediation=(rule.fix or {}).get("description"),
    )


def scan_frontmatter(rule: Rule, file_path: str, file_text: str) -> list[Finding]:
    pattern = rule.pattern
    fm_text, _ = _split_frontmatter(file_text)
    if fm_text is None:
        if pattern.get("optional"):
            return []
        return [_emit(rule, file_path, "missing or malformed YAML frontmatter")]

    try:
        parsed = yaml.safe_load(fm_text)
    except yaml.YAMLError as exc:
        return [_emit(rule, file_path, f"frontmatter not valid YAML: {exc}")]

    if not isinstance(parsed, dict):
        return [_emit(rule, file_path, "frontmatter must be a mapping")]

    findings: list[Finding] = []
    findings.extend(_validate_top_level(rule, file_path, parsed))
    findings.extend(_validate_field(rule, file_path, parsed))
    findings.extend(_validate_field_path(rule, file_path, parsed))
    return findings


def _validate_top_level(rule: Rule, file_path: str, data: dict[str, Any]) -> list[Finding]:
    allowed = rule.pattern.get("forbid_top_level_fields_outside")
    if not allowed:
        return []
    allowed_set = set(allowed)
    extra = sorted(k for k in data if k not in allowed_set)
    if not extra:
        return []
    return [
        _emit(
            rule,
            file_path,
            f"non-canonical top-level fields: {', '.join(extra)}",
        )
    ]


def _validate_field(rule: Rule, file_path: str, data: dict[str, Any]) -> list[Finding]:
    field = rule.pattern.get("field")
    if not field:
        return []
    optional = bool(rule.pattern.get("optional", False))
    if field not in data:
        if optional:
            return []
        return [_emit(rule, file_path, f"required field {field!r} missing")]
    value = data[field]

    findings: list[Finding] = []
    must_match = rule.pattern.get("must_match")
    if must_match and (not isinstance(value, str) or not re.fullmatch(str(must_match), value)):
        findings.append(_emit(rule, file_path, f"{field!r} does not match {must_match!r}"))

    max_len = rule.pattern.get("max_length")
    if max_len is not None and isinstance(value, str) and len(value) > int(max_len):
        findings.append(_emit(rule, file_path, f"{field!r} exceeds max length {max_len}"))

    min_len = rule.pattern.get("min_length")
    if min_len is not None and (not isinstance(value, str) or len(value) < int(min_len)):
        findings.append(_emit(rule, file_path, f"{field!r} below min length {min_len}"))

    forbid_tokens = rule.pattern.get("forbid_tokens")
    if forbid_tokens and isinstance(value, str):
        lowered = value.lower()
        for token in forbid_tokens:
            if str(token).lower() in lowered:
                findings.append(
                    _emit(rule, file_path, f"{field!r} contains forbidden token {token!r}")
                )

    if (
        rule.pattern.get("must_match_spdx")
        and isinstance(value, str)
        and not is_valid_spdx(value)
    ):
        findings.append(
            _emit(rule, file_path, f"{field!r}={value!r} is not a recognised SPDX identifier")
        )

    return findings


def _validate_field_path(rule: Rule, file_path: str, data: dict[str, Any]) -> list[Finding]:
    path = rule.pattern.get("field_path")
    if not path:
        return []
    must_be_absent = bool(rule.pattern.get("must_be_absent"))
    found, _value = _resolve_path(data, str(path))
    if must_be_absent and found:
        return [_emit(rule, file_path, f"{path!r} must be absent")]
    if not must_be_absent and not found:
        return [_emit(rule, file_path, f"{path!r} required but missing")]
    return []
