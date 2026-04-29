"""Pruner Verified badge SVG emitter.

Coroboros Design Direction:
  - Void background ``#000000``.
  - JetBrains Mono typeface.
  - No gradient, no shadow, no rounded corners.
  - Grade A=#D4AF37, B=#C9A96E, C=#8B6914, D/F=#E53935.
  - Honest delegation in fine print: ``engine: cisco-ai-skill-scanner@<sha>``.
"""

from __future__ import annotations

GRADE_COLOR: dict[str, str] = {
    "A": "#D4AF37",
    "B": "#C9A96E",
    "C": "#8B6914",
    "D": "#E53935",
    "F": "#E53935",
}

DEFAULT_ENGINE_SHA = "f2858cf3"

_FONT = "JetBrains Mono, ui-monospace, Menlo, Consolas, monospace"


def render_badge_svg(*, grade: str, engine_sha: str | None = None) -> str:
    """Return an SVG string for the Pruner Verified badge."""

    grade = grade.upper() if grade else "F"
    color = GRADE_COLOR.get(grade, "#E53935")
    short_sha = (engine_sha or DEFAULT_ENGINE_SHA)[:8]

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg"',
        ' width="280" height="56" viewBox="0 0 280 56"',
        f' role="img" aria-label="Pruner Verified — grade {grade}">',
        f"<title>Pruner Verified — grade {grade}</title>",
        '<rect x="0" y="0" width="280" height="56" fill="#000000"/>',
        f'<text x="14" y="24" font-family="{_FONT}"',
        ' font-size="14" font-weight="700" fill="#FFFFFF">Pruner Verified</text>',
        f'<text x="180" y="24" font-family="{_FONT}"',
        f' font-size="14" font-weight="700" fill="{color}">Grade {grade}</text>',
        f'<text x="14" y="44" font-family="{_FONT}"',
        ' font-size="9" fill="#FFFFFF" fill-opacity="0.6">',
        f"engine: cisco-ai-skill-scanner@{short_sha}</text>",
        "</svg>",
    ]
    return "".join(parts)
