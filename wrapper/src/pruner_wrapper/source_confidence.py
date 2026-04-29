"""Map a file path to its `source_confidence` tag and weight.

Continuous weight, not tier downgrade. Higher-trust paths (active-runtime,
hook-code) keep severity at full weight; template / docs / test fixture
paths downgrade. Secrets and PI-UNI-* findings are weight-locked at 1.00.
"""

from __future__ import annotations

import fnmatch

from pruner_wrapper.types import SOURCE_CONFIDENCE_WEIGHT, SourceConfidence

# Ordered: more specific patterns first; first match wins.
PATH_RULES: tuple[tuple[str, SourceConfidence], ...] = (
    # active-runtime — files the agent loads as-is
    ("skills/*/SKILL.md", "active-runtime"),
    ("skills/*/scripts/*", "active-runtime"),
    ("skills/*/scripts/**", "active-runtime"),
    ("skills/*/references/*", "active-runtime"),
    ("skills/*/references/**", "active-runtime"),
    ("SKILL.md", "active-runtime"),
    # plugin-manifest
    (".claude-plugin/marketplace.json", "plugin-manifest"),
    (".claude-plugin/*", "plugin-manifest"),
    # project-local-optional
    (".pruner.local.yml", "project-local-optional"),
    (".pruner-policy.yml", "project-local-optional"),
    (".pruner-ignore.yml", "project-local-optional"),
    # template-example
    ("templates/*", "template-example"),
    ("templates/**", "template-example"),
    ("examples/*", "template-example"),
    ("examples/**", "template-example"),
    ("samples/*", "template-example"),
    ("samples/**", "template-example"),
    ("demo/**", "template-example"),
    ("playground/**", "template-example"),
    # docs-example
    ("docs/*", "docs-example"),
    ("docs/**", "docs-example"),
    ("guide/**", "docs-example"),
    ("tutorial/**", "docs-example"),
    ("cookbook/**", "docs-example"),
    # test-fixture
    ("tests/*", "test-fixture"),
    ("tests/**", "test-fixture"),
    ("**/fixtures/*", "test-fixture"),
    ("**/fixtures/**", "test-fixture"),
    ("**/__snapshots__/*", "test-fixture"),
    ("**/__snapshots__/**", "test-fixture"),
)


def _matches(path: str, pattern: str) -> bool:
    """Glob-match `path` against `pattern`. `**` is treated as recursive."""

    # fnmatch does not natively handle `**` for path components. Translate
    # `**/` to a sequence that matches zero or more path components.
    if "**" not in pattern:
        return fnmatch.fnmatch(path, pattern)

    # Manual segment matching for `**` patterns.
    parts_pattern = pattern.split("/")
    parts_path = path.split("/")
    return _segment_match(parts_path, parts_pattern)


def _segment_match(path_parts: list[str], pattern_parts: list[str]) -> bool:
    """Match path segments against glob-pattern segments with `**` support."""

    if not pattern_parts:
        return not path_parts
    head, *tail = pattern_parts
    if head == "**":
        if not tail:
            return True
        return any(_segment_match(path_parts[i:], tail) for i in range(len(path_parts) + 1))
    if not path_parts:
        return False
    if fnmatch.fnmatch(path_parts[0], head):
        return _segment_match(path_parts[1:], tail)
    return False


def classify(path: str) -> SourceConfidence:
    """Return the source-confidence tag for `path`.

    Defaults to `active-runtime` when no pattern matches — the conservative
    choice for unrecognised paths in a skill repo.
    """

    normalised = path[2:] if path.startswith("./") else path
    for pattern, tag in PATH_RULES:
        if _matches(normalised, pattern):
            return tag
    return "active-runtime"


def weight_for(path: str, override: float | None = None) -> float:
    """Return the effective weight for a finding at `path`.

    If `override` is set (e.g. PI-UNI-001's `weight_override: 1.00`), the
    override always wins regardless of path classification.
    """

    if override is not None:
        return float(override)
    return SOURCE_CONFIDENCE_WEIGHT[classify(path)]
