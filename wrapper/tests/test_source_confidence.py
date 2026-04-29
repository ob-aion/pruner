"""Tests for source-confidence path classification + weighting."""

from __future__ import annotations

from pruner_wrapper.source_confidence import classify, weight_for


def test_active_runtime_paths() -> None:
    assert classify("skills/foo/SKILL.md") == "active-runtime"
    assert classify("skills/foo/scripts/install.sh") == "active-runtime"


def test_template_paths() -> None:
    assert classify("templates/workflow.yml") == "template-example"
    assert classify("examples/vulnerable-skill/SKILL.md") == "template-example"


def test_docs_paths() -> None:
    assert classify("docs/threat-model.md") == "docs-example"


def test_test_fixture_paths() -> None:
    assert classify("tests/test_x.py") == "test-fixture"
    assert classify("wrapper/tests/fixtures/skill_a.md") == "test-fixture"


def test_plugin_manifest_paths() -> None:
    assert classify(".claude-plugin/marketplace.json") == "plugin-manifest"


def test_default_active_runtime() -> None:
    assert classify("some/random/file.md") == "active-runtime"


def test_weight_for_uses_classification() -> None:
    assert weight_for("skills/foo/SKILL.md") == 1.00
    assert weight_for("docs/x.md") == 0.25
    assert weight_for("tests/t.py") == 0.25


def test_weight_override_wins() -> None:
    assert weight_for("docs/x.md", override=1.00) == 1.00
    assert weight_for("skills/foo/SKILL.md", override=0.25) == 0.25
