"""Shared fixtures for pruner_wrapper tests."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest
import yaml

from pruner_wrapper.pack_runner import load_rule
from pruner_wrapper.types import Rule

TESTS_DIR = Path(__file__).parent
REPO_ROOT = TESTS_DIR.parent.parent
RULES_ROOT = REPO_ROOT / "rules"
SCHEMA_ROOT = REPO_ROOT / "schema"


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def rules_root() -> Path:
    return RULES_ROOT


@pytest.fixture(scope="session")
def schema_root() -> Path:
    return SCHEMA_ROOT


@pytest.fixture(scope="session")
def rule_v1_schema() -> dict[str, object]:
    return json.loads((SCHEMA_ROOT / "rule-v1.json").read_text())


@pytest.fixture(scope="session")
def rule_loader() -> Callable[[str], Rule]:
    """Return a function that loads a rule by ID from the on-disk pack."""

    cache: dict[str, Rule] = {}

    def _load(rule_id: str) -> Rule:
        if rule_id in cache:
            return cache[rule_id]
        for path in RULES_ROOT.rglob("*.yml"):
            try:
                raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            except yaml.YAMLError:
                continue
            if isinstance(raw, dict) and raw.get("id") == rule_id:
                rule = load_rule(path)
                cache[rule_id] = rule
                return rule
        raise FileNotFoundError(f"Rule {rule_id!r} not found under {RULES_ROOT}")

    return _load


@pytest.fixture
def fixtures_dir(tmp_path: Path) -> Path:
    return tmp_path
