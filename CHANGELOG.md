# Changelog

All notable changes are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Conventional Commits](https://www.conventionalcommits.org/). Versioning is [SemVer](https://semver.org/) — bare numbers, no `v` prefix.

## [Unreleased]

## [0.1.0] — 2026-04-29 — initial Loom

First public release. Coroboros's attestation chain over `cisco-ai-skill-scanner`.

### Added
- Composite GitHub Action `coroboros/pruner` wrapping `cisco-ai-skill-scanner@2.0.9` (Apache-2.0, fully local) as the detection backend, plus `gitleaks` for secrets and `actionlint` for the audited repo's workflows.
- Coroboros policy pack — 12 default-on rules:
  - **FC001–FC005** frontmatter conformance for the agentskills.io spec (kebab-case names, description length, custom-fields-under-metadata, `metadata.version` forbidden, SPDX license).
  - **PI-UNI-001..004** Unicode-Tag arsenal (Tag block U+E0000–U+E007F, variation selectors, bidi override / Trojan Source, homoglyph instruction tokens).
  - **PI-PEP723-001** PEP-723 inline-deps without pin operators.
  - **PI-IDFILE-001** scripts writing to identity / persistence files.
  - **PI-MDIMG-001** markdown-image data-exfil syntax.
- Coroboros policy pack — 12 opt-in PD rules (PD001–PD012) for prompt-defense posture on generalist-agent prompt files. Gated by `.pruner-policy.yml` `scan_prompt_defense_posture: true`.
- Wrapper Python package `pruner-wrapper` (Apache-2.0, runtime deps: `pyyaml` + `cisco-ai-skill-scanner` pinned + stdlib).
- Schema contracts `schema/rule-v1.json`, `schema/report-v1.json`, `schema/allowlist-v1.json`, `schema/policy-v1.json` (JSON Schema 2020-12).
- Attestation chain via `actions/attest-build-provenance` + `actions/attest-sbom` against the public-good Sigstore instance and GitHub OIDC. Bundle delivered to release assets; consumers verify with `gh attestation verify`.
- Pruner Verified badge SVG aligned with Coroboros Design Direction (Void background, JetBrains Mono, no gradient/shadow/rounded corners).
- Reusable workflow `.github/workflows/reusable-full-scan.yml` for one-line consumer integration.
- Self-scan workflow — Pruner audits Pruner on every push.
- OpenSSF Scorecard weekly + on tag.
- Monthly Cisco upstream health probe.
- Examples `examples/vulnerable-skill/` and `examples/benign-skill/` with `EXPECTATIONS.md` cross-walks.
- Documentation: threat model, why-cisco, coverage matrix, FP audit on three public skill repos (`coroboros/agent-skills`, `anthropics/skills`, `vercel-labs/agent-skills`), writing-rules, consumer-integration, verify-a-report.

### Status
Experimental. Bus factor 1. Honest delegation: detection is Cisco's, policy and signature are Coroboros's.

[Unreleased]: https://github.com/coroboros/pruner/compare/0.1.0...HEAD
[0.1.0]: https://github.com/coroboros/pruner/releases/tag/0.1.0
