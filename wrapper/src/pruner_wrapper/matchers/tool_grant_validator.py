"""Tool-grant validator — `pattern.type: tool-grant-validator`.

PI-PERM-001 fires when a SKILL.md declares an `allowed-tools` set that
omits `Bash` (or a wildcard equivalent) yet ships scripts that invoke
shell or subprocess. Cross-file by design: needs the skill folder layout
to know which scripts to inspect. Receives the scan tree root via the
shared scan-context set in `pack_runner.scan_tree`.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

import yaml

from pruner_wrapper.matchers._context import context_skip
from pruner_wrapper.matchers.frontmatter_validator import _split_frontmatter
from pruner_wrapper.types import Finding, Location, Rule

_BASH_WILDCARDS = {"Bash", "bash", "*"}
_PY_SUBPROCESS_MODULES = {"subprocess", "pty"}
_PY_OS_EXEC_FUNCS = {
    "system",
    "popen",
    "execv",
    "execve",
    "execvp",
    "execvpe",
    "spawnv",
    "spawnvp",
    "spawnve",
    "spawnvpe",
}
_BASH_NOOP_RE = re.compile(r"^\s*(#|set\s|set$|export\s|[A-Z_]+=.*$|$)")


def _parse_allowed_tools(value: Any) -> list[str]:
    """Parse `allowed-tools` into a flat list of declared grants."""

    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        return [s.strip() for s in value.split(",") if s.strip()]
    return []


def _grants_bash(allowed: list[str]) -> bool:
    """Return True if the allowed-tools declaration grants shell access."""

    for tool in allowed:
        if tool in _BASH_WILDCARDS or tool.startswith("Bash(") or tool.startswith("bash("):
            return True
    return False


def _python_uses_shell(source: str) -> bool:
    """Return True if Python imports subprocess/pty or calls os.system/popen/exec*."""

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in _PY_SUBPROCESS_MODULES:
                    return True
        elif isinstance(node, ast.ImportFrom):
            if node.module in _PY_SUBPROCESS_MODULES:
                return True
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            target = node.func
            if (
                isinstance(target.value, ast.Name)
                and target.value.id == "os"
                and target.attr in _PY_OS_EXEC_FUNCS
            ):
                return True
    return False


def _bash_executes(source: str) -> bool:
    """Return True if a `.sh` file contains at least one executable line.

    Comments, shebangs, blank lines, `set` directives, and bare variable
    assignments do not count as execution.
    """

    for raw in source.splitlines():
        if _BASH_NOOP_RE.match(raw):
            continue
        if raw.strip().startswith("#!"):
            continue
        return True
    return False


def _walk_scripts(skill_dir: Path) -> tuple[Path | None, str]:
    """Return the first script that triggers the rule, plus a one-line reason."""

    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.is_dir():
        return None, ""

    for py_file in sorted(scripts_dir.rglob("*.py")):
        try:
            text = py_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if _python_uses_shell(text):
            return py_file, "imports subprocess/pty or calls os.system/os.popen/os.exec*"

    for sh_file in sorted(scripts_dir.rglob("*.sh")):
        try:
            text = sh_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if _bash_executes(text):
            return sh_file, "contains executable shell commands"

    return None, ""


def scan_tool_grant(rule: Rule, file_path: str, file_text: str) -> list[Finding]:
    """Cross-file rule: SKILL.md frontmatter vs sibling scripts/."""

    if context_skip(rule.context_rules, path=file_path):
        return []

    fm_text, _ = _split_frontmatter(file_text)
    if fm_text is None:
        return []
    try:
        parsed = yaml.safe_load(fm_text)
    except yaml.YAMLError:
        return []
    if not isinstance(parsed, dict):
        return []

    declared = _parse_allowed_tools(parsed.get("allowed-tools"))
    if not declared:
        return []
    if _grants_bash(declared):
        return []

    from pruner_wrapper.pack_runner import get_scan_context

    tree_root = get_scan_context().get("tree_root")
    if not isinstance(tree_root, Path):
        return []

    skill_dir = (tree_root / file_path).resolve().parent
    if not skill_dir.exists():
        return []

    script_path, reason = _walk_scripts(skill_dir)
    if script_path is None:
        return []

    rel = script_path.relative_to(tree_root).as_posix()
    return [
        Finding(
            id=rule.id,
            category=rule.category,
            severity_declared=rule.severity,
            severity_effective=rule.severity,
            tool="pruner-wrapper",
            location=Location(path=file_path, line=1, start_column=1, end_column=1),
            message=(
                f"{rule.title} — {rel} {reason}; declared allowed-tools: "
                f"{', '.join(declared)}"
            ),
            owasp_ref=rule.owasp_ref,
            owasp_ast=rule.owasp_ast,
            evidence_snippet=", ".join(declared),
            rationale_ref=rule.references[0] if rule.references else None,
            remediation=(rule.fix or {}).get("description"),
        )
    ]
