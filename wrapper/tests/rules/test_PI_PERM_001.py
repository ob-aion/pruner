"""PI-PERM-001 — allowed-tools mismatch (cross-file matcher)."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

from pruner_wrapper.pack_runner import scan_tree
from pruner_wrapper.types import Rule
from tests.rules._helpers import assert_yaml_valid

SKILL_NO_BASH = """---
name: "code-formatter"
description: "Formats Python files."
allowed-tools: Read,Edit
license: "Apache-2.0"
metadata:
  author: coroboros
---

# Formatter
"""

SKILL_WITH_BASH = """---
name: "code-formatter"
description: "Formats Python files."
allowed-tools: Read,Edit,Bash
license: "Apache-2.0"
metadata:
  author: coroboros
---

# Formatter
"""

SCRIPT_PY_USES_SUBPROCESS = """import subprocess


def run() -> None:
    subprocess.run(["black", "src"], check=True)
"""

SCRIPT_SH_EXECUTES = """#!/usr/bin/env bash
set -euo pipefail
black src
isort src
"""

SCRIPT_SH_NOOP = """#!/usr/bin/env bash
# Documentation-only script.
"""


def test_yaml_validates_against_schema(
    rule_v1_schema: dict[str, Any], rules_root: Any
) -> None:
    raw = yaml.safe_load(
        (rules_root / "permissions" / "PI-PERM-001-allowed-tools-mismatch.yml")
        .read_text(encoding="utf-8")
    )
    assert_yaml_valid(raw, rule_v1_schema)


def _make_skill(tmp_path: Path, skill_md: str, script: tuple[str, str] | None) -> Path:
    """Build a tmp `skills/x/` layout. Returns the tree root."""

    root = tmp_path / "tree"
    skill_dir = root / "skills" / "demo"
    (skill_dir / "scripts").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    if script is not None:
        name, body = script
        (skill_dir / "scripts" / name).write_text(body, encoding="utf-8")
    return root


def test_skill_without_bash_grant_and_python_subprocess_fires(
    rule_loader: Callable[[str], Rule], tmp_path: Path
) -> None:
    rule = rule_loader("PI-PERM-001")
    root = _make_skill(tmp_path, SKILL_NO_BASH, ("install.py", SCRIPT_PY_USES_SUBPROCESS))
    findings = scan_tree(root=root, rules=[rule])
    assert any(f.id == "PI-PERM-001" for f in findings), findings


def test_skill_without_bash_grant_and_executable_sh_fires(
    rule_loader: Callable[[str], Rule], tmp_path: Path
) -> None:
    rule = rule_loader("PI-PERM-001")
    root = _make_skill(tmp_path, SKILL_NO_BASH, ("install.sh", SCRIPT_SH_EXECUTES))
    findings = scan_tree(root=root, rules=[rule])
    assert any(f.id == "PI-PERM-001" for f in findings), findings


def test_skill_with_bash_grant_does_not_fire(
    rule_loader: Callable[[str], Rule], tmp_path: Path
) -> None:
    rule = rule_loader("PI-PERM-001")
    root = _make_skill(tmp_path, SKILL_WITH_BASH, ("install.sh", SCRIPT_SH_EXECUTES))
    findings = scan_tree(root=root, rules=[rule])
    assert not [f for f in findings if f.id == "PI-PERM-001"], findings


def test_noop_script_does_not_fire(
    rule_loader: Callable[[str], Rule], tmp_path: Path
) -> None:
    rule = rule_loader("PI-PERM-001")
    root = _make_skill(tmp_path, SKILL_NO_BASH, ("install.sh", SCRIPT_SH_NOOP))
    findings = scan_tree(root=root, rules=[rule])
    assert not [f for f in findings if f.id == "PI-PERM-001"], findings


def test_no_scripts_directory_does_not_fire(
    rule_loader: Callable[[str], Rule], tmp_path: Path
) -> None:
    rule = rule_loader("PI-PERM-001")
    root = _make_skill(tmp_path, SKILL_NO_BASH, None)
    findings = scan_tree(root=root, rules=[rule])
    assert not [f for f in findings if f.id == "PI-PERM-001"], findings
