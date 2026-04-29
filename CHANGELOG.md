# Changelog

## v0.1.2 - 29/04/2026

Suppresses a gitleaks false positive that blocked the 0.1.1 release pipeline. First release with the signed attestation bundle attached.

- Added `.gitleaksignore` with the fingerprint for `wrapper/tests/test_policy.py:69`. The `generic-api-key` rule pattern-matched a Python keyword argument (`severity_declared="..."` adjacent to the literal `secrets`) — no actual credential was present. Suppression is fingerprint-scoped with a written justification in the file.

## v0.1.1 - 29/04/2026

Maintenance release fixing CI issues that blocked 0.1.0 from attaching the signed attestation bundle to the release.

- Repo transferred from `coroboros/pruner` to `ob-aion/pruner` to bypass the `gitleaks-action` paid-license requirement for org-owned repositories.
- Replaced `gitleaks/gitleaks-action@v2.3.x` with the gitleaks CLI fetched directly from upstream releases (MIT, no license check). SHA256-pinned to `v8.30.1`.
- Install `snyk` binary via `npm install -g snyk` when `with-snyk: true && SNYK_TOKEN != ''`. Eliminates the silent no-op for consumers using the reusable workflow.
- Tightened `release.yml` permissions per OpenSSF Scorecard — top-level read-only, write declared at job-level only.
- `scorecard.yml` no longer triggers on tag pushes — `ossf/scorecard-action` only supports the default branch.
- README and `docs/consumer-integration.md` document the Snyk second-opinion opt-in path explicitly.

0.1.1 is the first release with the signed attestation bundle and badge SVG attached to the GitHub release.

## v0.1.0 - 29/04/2026

Initial release of Pruner — Coroboros's attestation chain for agent skill repositories.

- Composite GitHub Action wrapping `cisco-ai-skill-scanner@2.0.9` (Apache-2.0, fully local) plus `gitleaks` for secrets and `actionlint` for the audited repo's workflows. Every external `uses:` SHA-pinned.
- Coroboros policy pack — 12 default-on rules: frontmatter conformance (FC001-FC005), Unicode-Tag arsenal (PI-UNI-001..004), supply-chain hygiene (PI-PEP723-001, PI-IDFILE-001, PI-MDIMG-001).
- Coroboros policy pack — 12 opt-in PD rules (PD001-PD012) for prompt-defense posture on generalist-agent prompt files. Gated by `.pruner-policy.yml` `scan_prompt_defense_posture: true`.
- Attestation chain via `actions/attest-build-provenance` + `actions/attest-sbom` against public-good Sigstore and GitHub OIDC. Bundle verifiable with `gh attestation verify`.
- Pruner Verified badge SVG aligned with Coroboros Design Direction (Void background, JetBrains Mono, no gradient/shadow/rounded corners).
- Schema contracts at `schema/{rule-v1,report-v1,allowlist-v1,policy-v1}.json` (JSON Schema 2020-12).
- Reusable workflow `.github/workflows/reusable-full-scan.yml` for one-line consumer integration.
- Self-scan workflow — Pruner audits Pruner on every push.
- OpenSSF Scorecard weekly + on tag.
- Monthly Cisco upstream-monitoring cron.
- Documentation: threat model, why-cisco, coverage matrix, FP audit on `coroboros/agent-skills` + `anthropics/skills` + `vercel-labs/agent-skills`, writing-rules, consumer-integration, verify-a-report.
