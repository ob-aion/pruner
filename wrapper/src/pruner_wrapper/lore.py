"""Lore strings used by the terminal formatter.

Outsiders read plain English; insiders recognise the references. ASCII-only.
"""

from __future__ import annotations

LORE: dict[str, str] = {
    "scan_start": "Pruning variants at threshold: {threshold}",
    "scan_clean": "No variants detected in this timeline.",
    "scan_below_threshold": "{count} variants below threshold. Observed.",
    "scan_critical": "Temporal deviation detected. Variant pruned at threshold.",
    "scan_unstable": "Timeline unstable. Review required.",
    "cisco_engaged": "Loom thread engaged: cisco-ai-skill-scanner@{sha}",
    "cisco_drift": "Temporal deviation in upstream. Engine license drifted; halt.",
    "cisco_stale": "The Loom is fraying. Upstream check required.",
    "release_first": "Loom integrated. For all skills. Always.",
    "release_green": "Branch stabilised.",
    "release_allowlisted": "Branch stabilised. {count} variants acknowledged at the threshold.",
    "config_error": "Temporal deviation in configuration. The Loom cannot run.",
    "missing_input": "Signal lost. Required input: {field}",
    "wrapper_crash": "The Loom has faltered. Issue: {message}",
    "report_footer": "This timeline is stable.",
}


def message(key: str, **fmt: str | int) -> str:
    """Look up a lore string and format it with `fmt`. Falls back to `key`."""

    template = LORE.get(key, key)
    try:
        return template.format(**fmt)
    except (KeyError, IndexError):
        return template
