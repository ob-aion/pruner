"""PEP-723 validator — `pattern.type: pep723-validator`.

Detects `# /// script` ... `# ///` blocks where `dependencies` declarations
lack the required pin operator (default `==`). Per PI-PEP723-001.
"""

from __future__ import annotations

import re

from pruner_wrapper.matchers._context import context_skip
from pruner_wrapper.types import Finding, Location, Rule

_BLOCK_RE = re.compile(r"^# /// script\s*$(.*?)^# ///\s*$", re.MULTILINE | re.DOTALL)
_DEP_LIST_RE = re.compile(r"dependencies\s*=\s*\[(.*?)\]", re.DOTALL)
_QUOTED_DEP_RE = re.compile(r"['\"]([^'\"]+)['\"]")


def _strip_comment_prefix(block_body: str) -> str:
    """Remove the leading `#` from each line of a PEP-723 metadata block."""

    out_lines: list[str] = []
    for raw in block_body.splitlines():
        stripped = raw.lstrip()
        if stripped.startswith("# "):
            out_lines.append(stripped[2:])
        elif stripped.startswith("#"):
            out_lines.append(stripped[1:])
        else:
            out_lines.append(raw)
    return "\n".join(out_lines)


def scan_pep723(rule: Rule, file_path: str, file_text: str) -> list[Finding]:
    require_ops: list[str] = list(rule.pattern.get("require_pin_operator") or ["=="])
    if context_skip(rule.context_rules, path=file_path):
        return []

    findings: list[Finding] = []
    for block_match in _BLOCK_RE.finditer(file_text):
        body = _strip_comment_prefix(block_match.group(1))
        deps_match = _DEP_LIST_RE.search(body)
        if deps_match is None:
            continue
        deps_segment = deps_match.group(1)

        block_start_line = file_text.count("\n", 0, block_match.start()) + 1

        for dep_match in _QUOTED_DEP_RE.finditer(deps_segment):
            dep = dep_match.group(1).strip()
            if not dep:
                continue
            if any(op in dep for op in require_ops):
                continue
            findings.append(
                Finding(
                    id=rule.id,
                    category=rule.category,
                    severity_declared=rule.severity,
                    severity_effective=rule.severity,
                    tool="pruner-wrapper",
                    location=Location(
                        path=file_path,
                        line=block_start_line,
                        start_column=1,
                        end_column=1,
                    ),
                    message=f"{rule.title} — {dep!r} not pinned",
                    owasp_ref=rule.owasp_ref,
                    owasp_ast=rule.owasp_ast,
                    evidence_snippet=dep,
                    rationale_ref=rule.references[0] if rule.references else None,
                    remediation=(rule.fix or {}).get("description"),
                )
            )
    return findings
