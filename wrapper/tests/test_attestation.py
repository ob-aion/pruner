"""Tests for the attestation block emitter."""

from __future__ import annotations

from pruner_wrapper.attestation import attestation_block


def test_block_with_tag() -> None:
    block = attestation_block(repo="coroboros/pruner", tag="0.1.0")
    assert block["sbom_url"].endswith("/releases/download/0.1.0/sbom.cdx.json")
    assert block["verification_command"].startswith("gh attestation verify")
    assert "--owner coroboros" in block["verification_command"]


def test_block_without_tag() -> None:
    block = attestation_block(repo="coroboros/pruner")
    assert "/releases/download/latest/" in block["sbom_url"]
