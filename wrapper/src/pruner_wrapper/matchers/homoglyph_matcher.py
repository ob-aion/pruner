"""Homoglyph matcher — `pattern.type: homoglyph-instruction`.

For PI-UNI-004. Each `target_token` in `pattern.target_tokens` is expanded
into the set of mixed-script lookalikes using the inline confusables table;
matches are emitted with bounded regex word-boundaries.
"""

from __future__ import annotations

import re
from itertools import product

from pruner_wrapper.confusables import ASCII_TO_CONFUSABLES
from pruner_wrapper.matchers._context import (
    context_skip,
    fenced_block_lang_for_line,
    line_for_offset,
)
from pruner_wrapper.types import Finding, Location, Rule

_MAX_VARIANTS_PER_TOKEN = 64


def _generate_variants(token: str) -> set[str]:
    """Generate up to _MAX_VARIANTS_PER_TOKEN mixed-script lookalikes.

    Each character is expanded to (itself + confusables); products are filtered
    so that at least one position is non-ASCII and overall length matches.
    """

    char_choices: list[list[str]] = []
    for ch in token.lower():
        choices = [ch, *sorted(ASCII_TO_CONFUSABLES.get(ch, frozenset()))]
        char_choices.append(choices)

    variants: set[str] = set()
    for combo in product(*char_choices):
        candidate = "".join(combo)
        if candidate == token.lower():
            continue
        variants.add(candidate)
        if len(variants) >= _MAX_VARIANTS_PER_TOKEN:
            break
    return variants


def _word_boundary_re(variant: str) -> re.Pattern[str]:
    """Return a regex matching `variant` between word boundaries."""

    return re.compile(rf"(?<![A-Za-z]){re.escape(variant)}(?![A-Za-z])", re.IGNORECASE)


def scan_homoglyph(rule: Rule, file_path: str, file_text: str) -> list[Finding]:
    target_tokens: list[str] = list(rule.pattern.get("target_tokens") or [])
    if not target_tokens:
        return []

    findings: list[Finding] = []
    seen_lines: set[int] = set()

    for token in target_tokens:
        for variant in _generate_variants(token):
            compiled = _word_boundary_re(variant)
            for match in compiled.finditer(file_text):
                line_num, column = line_for_offset(file_text, match.start())
                if line_num in seen_lines:
                    continue
                line_text = (
                    file_text.splitlines()[line_num - 1]
                    if line_num <= len(file_text.splitlines())
                    else ""
                )
                fenced_lang = fenced_block_lang_for_line(file_text, line_num)
                if context_skip(
                    rule.context_rules,
                    path=file_path,
                    line_text=line_text,
                    fenced_lang=fenced_lang,
                ):
                    continue
                seen_lines.add(line_num)
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
                            end_column=column + len(variant),
                        ),
                        message=f"{rule.title} — token {token!r} as {variant!r}",
                        owasp_ref=rule.owasp_ref,
                        owasp_ast=rule.owasp_ast,
                        evidence_snippet=line_text.strip()[:200],
                        rationale_ref=rule.references[0] if rule.references else None,
                        remediation=(rule.fix or {}).get("description"),
                    )
                )
    return findings
