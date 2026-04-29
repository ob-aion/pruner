"""Regex matcher — `pattern.type: regex`."""

from __future__ import annotations

import re

from pruner_wrapper.matchers._context import (
    context_skip,
    fenced_block_lang_for_line,
    line_for_offset,
)
from pruner_wrapper.types import Finding, Location, Rule


def scan_regex(rule: Rule, file_path: str, file_text: str) -> list[Finding]:
    """Find all regex matches; emit one Finding per match (deduped by line)."""

    pattern_value = str(rule.pattern.get("value", ""))
    if not pattern_value:
        return []

    try:
        compiled = re.compile(pattern_value, re.MULTILINE)
    except re.error:
        return []

    ignore_in_fenced_blocks = bool(rule.scope.get("ignore_in_fenced_blocks", False))
    findings: list[Finding] = []
    seen_lines: set[int] = set()

    for match in compiled.finditer(file_text):
        line_num, column = line_for_offset(file_text, match.start())
        if line_num in seen_lines:
            continue
        seen_lines.add(line_num)

        line_text = file_text.splitlines()[line_num - 1] if line_num <= len(
            file_text.splitlines()
        ) else ""
        fenced_lang = fenced_block_lang_for_line(file_text, line_num)
        if ignore_in_fenced_blocks and fenced_lang is not None:
            continue
        if context_skip(
            rule.context_rules,
            path=file_path,
            line_text=line_text,
            fenced_lang=fenced_lang,
        ):
            continue

        end_col = column + (match.end() - match.start())
        findings.append(
            Finding(
                id=rule.id,
                category=rule.category,
                severity_declared=rule.severity,
                severity_effective=rule.severity,
                tool="pruner-wrapper",
                location=Location(
                    path=file_path,
                    line=line_num,
                    start_column=column,
                    end_column=end_col,
                ),
                message=f"{rule.title}",
                owasp_ref=rule.owasp_ref,
                owasp_ast=rule.owasp_ast,
                evidence_snippet=line_text.strip()[:200],
                rationale_ref=rule.references[0] if rule.references else None,
                remediation=(rule.fix or {}).get("description"),
            )
        )
    return findings
