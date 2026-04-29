"""Absence-regex matcher — `pattern.type: absence-regex`.

Used by the PD pack: trigger when defensive language is MISSING from a
generalist-agent prompt file. Combines:
  - `pattern.must_contain_any: [...defensive keywords...]` (any single match suppresses the finding)
  - `pattern.activation_gate.frontmatter_description_match`: only fire if the
    frontmatter `description` matches a generalist-agent verb pattern.

Without an activation gate, an absence-regex rule on every utility skill would
flood the report. With it, only generalist agents that advertise broad
capability and lack defensive language are flagged.
"""

from __future__ import annotations

import re
from typing import Any, cast

import yaml

from pruner_wrapper.types import Finding, Location, Rule


def _extract_frontmatter_description(text: str) -> str | None:
    """Pull `description` from a `---`-delimited YAML frontmatter block."""

    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    raw = text[3:end]
    try:
        loaded = yaml.safe_load(raw)
    except yaml.YAMLError:
        return None
    if not isinstance(loaded, dict):
        return None
    desc = loaded.get("description")
    return desc if isinstance(desc, str) else None


def scan_absence_regex(rule: Rule, file_path: str, file_text: str) -> list[Finding]:
    """Emit one finding when defensive language is missing under the gate."""

    pattern = rule.pattern
    must_contain_any: list[str] = list(pattern.get("must_contain_any") or [])
    if not must_contain_any:
        return []

    gate_raw = cast(dict[str, Any], pattern.get("activation_gate") or {})
    description_pattern = gate_raw.get("frontmatter_description_match")
    if description_pattern:
        desc = _extract_frontmatter_description(file_text) or ""
        try:
            if not re.search(str(description_pattern), desc, flags=re.IGNORECASE):
                return []
        except re.error:
            return []

    body = file_text.lower()
    for keyword in must_contain_any:
        if keyword.lower() in body:
            return []

    return [
        Finding(
            id=rule.id,
            category=rule.category,
            severity_declared=rule.severity,
            severity_effective=rule.severity,
            tool="pruner-wrapper",
            location=Location(path=file_path, line=1, start_column=1, end_column=1),
            message=rule.title,
            owasp_ref=rule.owasp_ref,
            owasp_ast=rule.owasp_ast,
            evidence_snippet="",
            rationale_ref=rule.references[0] if rule.references else None,
            remediation=(rule.fix or {}).get("description"),
        )
    ]
