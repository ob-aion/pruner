"""Tests for the PEP-723 validator."""

from __future__ import annotations

from pruner_wrapper.matchers.pep723_validator import scan_pep723
from pruner_wrapper.types import Rule


def _rule(require: list[str] | None = None) -> Rule:
    pattern: dict[str, object] = {"type": "pep723-validator"}
    if require is not None:
        pattern["require_pin_operator"] = require
    return Rule(
        id="PI-PEP723-001",
        slug="x",
        title="t",
        severity="high",
        category="supply-chain",
        pattern=pattern,
        rationale="r",
        fixtures={"positive": [], "negative": []},
        scope={"file_patterns": ["**/*.py"]},
        status="stable",
        since="0.1.0",
    )


PINNED = """# /// script
# dependencies = ["requests==2.31.0"]
# ///
"""

UNPINNED = """# /// script
# dependencies = ["requests"]
# ///
"""

MIXED = """# /// script
# dependencies = ["requests==2.31.0", "rich"]
# ///
"""


def test_pinned_passes() -> None:
    assert scan_pep723(_rule(), "a.py", PINNED) == []


def test_unpinned_fires() -> None:
    findings = scan_pep723(_rule(), "a.py", UNPINNED)
    assert len(findings) == 1


def test_mixed_only_fires_for_unpinned() -> None:
    findings = scan_pep723(_rule(), "a.py", MIXED)
    assert len(findings) == 1
    assert "rich" in findings[0].message


def test_no_pep723_block_returns_empty() -> None:
    assert scan_pep723(_rule(), "a.py", "import os\n") == []


def test_custom_pin_operators() -> None:
    rule = _rule(require=[">="])
    text = """# /// script
# dependencies = ["requests>=2.31"]
# ///
"""
    assert scan_pep723(rule, "a.py", text) == []


def test_context_skip_path() -> None:
    rule = _rule()
    rule.context_rules = {"skip_if_path_matches": ["**/test_*.py"]}
    assert scan_pep723(rule, "tests/test_a.py", UNPINNED) == []
