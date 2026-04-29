"""Codepoint-range matcher — `pattern.type: codepoint-range`.

PI-UNI-001/002/003 use this. Streams chars, tracks line/column, optionally
applies a clustering threshold (PI-UNI-002 fires on ≥4 selectors clustered).
"""

from __future__ import annotations

from pruner_wrapper.matchers._context import context_skip, fenced_block_lang_for_line
from pruner_wrapper.types import Finding, Location, Rule


def _parse_ranges(raw: list[list[str]]) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for entry in raw:
        if len(entry) != 2:
            continue
        try:
            lo = int(entry[0], 16)
            hi = int(entry[1], 16)
        except ValueError:
            continue
        if lo <= hi:
            out.append((lo, hi))
    return out


def _in_any(cp: int, ranges: list[tuple[int, int]]) -> bool:
    return any(lo <= cp <= hi for lo, hi in ranges)


def scan_codepoint_range(rule: Rule, file_path: str, file_text: str) -> list[Finding]:
    """Emit findings on hits inside any of the configured codepoint ranges."""

    raw_ranges = list(rule.pattern.get("ranges") or [])
    ranges = _parse_ranges(raw_ranges)
    if not ranges:
        return []

    threshold = int(rule.pattern.get("threshold", 1))
    ignore_in_fenced_blocks = bool(rule.scope.get("ignore_in_fenced_blocks", False))

    findings: list[Finding] = []

    def _emit(start: tuple[int, int], end: tuple[int, int]) -> None:
        line_num_ = start[0]
        lines = file_text.splitlines()
        line_text = lines[line_num_ - 1] if line_num_ <= len(lines) else ""
        fenced_lang = fenced_block_lang_for_line(file_text, line_num_)
        if ignore_in_fenced_blocks and fenced_lang is not None:
            return
        if context_skip(
            rule.context_rules,
            path=file_path,
            line_text=line_text,
            fenced_lang=fenced_lang,
        ):
            return
        findings.append(
            Finding(
                id=rule.id,
                category=rule.category,
                severity_declared=rule.severity,
                severity_effective=rule.severity,
                tool="pruner-wrapper",
                location=Location(
                    path=file_path,
                    line=line_num_,
                    start_column=start[1],
                    end_column=end[1] + 1,
                ),
                message=rule.title,
                owasp_ref=rule.owasp_ref,
                owasp_ast=rule.owasp_ast,
                evidence_snippet=_hex_dump(file_text, start, end),
                rationale_ref=rule.references[0] if rule.references else None,
                remediation=(rule.fix or {}).get("description"),
            )
        )

    cluster: list[tuple[int, int]] = []
    cluster_start: tuple[int, int] | None = None
    line_num = 1
    column = 0

    for ch in file_text:
        column += 1
        cp = ord(ch)
        if _in_any(cp, ranges):
            if not cluster:
                cluster_start = (line_num, column)
            cluster.append((line_num, column))
        else:
            if cluster and len(cluster) >= threshold and cluster_start is not None:
                _emit(cluster_start, cluster[-1])
            cluster = []
            cluster_start = None
        if ch == "\n":
            if cluster and len(cluster) >= threshold and cluster_start is not None:
                _emit(cluster_start, cluster[-1])
            cluster = []
            cluster_start = None
            line_num += 1
            column = 0

    if cluster and len(cluster) >= threshold and cluster_start is not None:
        _emit(cluster_start, cluster[-1])

    return findings


def _hex_dump(text: str, start: tuple[int, int], end: tuple[int, int]) -> str:
    """Hex-dump the codepoints inside a cluster (best-effort). Truncates at 8 chars."""

    line_num = start[0]
    lines = text.splitlines()
    if line_num > len(lines):
        return ""
    line = lines[line_num - 1]
    s = max(0, start[1] - 1)
    e = min(len(line), end[1])
    span = line[s:e]
    return " ".join(f"U+{ord(c):04X}" for c in span[:8])
