"""Populate the `attestation` block of `report-v1.json` with verification metadata."""

from __future__ import annotations

from typing import Any


def attestation_block(
    *,
    repo: str,
    tag: str | None = None,
    bundle_filename: str = "pruner-report.zip",
) -> dict[str, Any]:
    """Return an `attestation` sub-document for inclusion in the report.

    URLs follow the GitHub release-asset convention. Filled in by the release
    workflow once the assets exist; consumers verify with `gh attestation verify`.
    """

    base = f"https://github.com/{repo}"
    tag_segment = tag if tag else "latest"
    return {
        "provenance_url": f"{base}/attestations",
        "sbom_url": f"{base}/releases/download/{tag_segment}/sbom.cdx.json",
        "verification_command": (
            f"gh attestation verify {bundle_filename} --owner {repo.split('/')[0]}"
        ),
    }
