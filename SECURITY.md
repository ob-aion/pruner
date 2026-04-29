# Security Policy

## Reporting a vulnerability

Open a private vulnerability report at <https://github.com/coroboros/pruner/security/advisories/new>. Do not file a public issue. Do not email.

**SLA**

- Acknowledge: 72 hours
- Triage: 7 days
- Fix critical: 30 days
- Fix high: 90 days

CVE requested via GitHub Security Advisories when warranted.

## Threat model

Pruner is a CI-only audit tool that runs on the publishing side of an agent skill repository. It does not execute scanned skills, does not load them into a runtime, does not phone home, and does not require network access for the deterministic phases.

**In scope**

- Static analysis of `SKILL.md`, frontmatter, `scripts/`, `references/`, `assets/`, and `.github/workflows/` files in the audited repo.
- Detection delegated to `cisco-ai-defense/skill-scanner` (Apache-2.0) under SHA pin, plus the Coroboros policy pack of 12 default-on rules + 12 opt-in PD rules.
- Secrets scanning via `gitleaks`.
- Workflow safety via `actionlint`.
- Attestation via `actions/attest-build-provenance` + `actions/attest-sbom`.

**Out of scope**

- Runtime monitoring of an agent that has loaded a skill.
- Sandboxed execution of scanned content.
- Consumer-machine `.claude/` configuration scanning.
- Taint or dataflow analysis (delegated to Cisco).
- Multimodal injection through fetched URLs (Pruner flags external URL references but does not fetch them).
- Latent semantic activation (delayed-trigger backdoors not visible from static text).

Full coverage matrix: [`docs/coverage-matrix.md`](./docs/coverage-matrix.md). FP-audit: [`docs/fp-audit.md`](./docs/fp-audit.md).

## Audit-the-auditor

Pruner's own attack surface is small but real:

- **Wrapper package (`pruner-wrapper`).** Runtime deps are `pyyaml` and `cisco-ai-skill-scanner` (the pinned engine). Stdlib otherwise. The dependency surface is reviewable in `wrapper/pyproject.toml`. Dependabot tracks bumps; CODEOWNERS-required review.
- **Cisco engine.** Apache-2.0, multi-thousand-LOC scanner. Pinned at `2.0.9`. License-drift check runs at install (`scripts/setup-cisco.sh`) and halts the action if the upstream license marker changes. Monthly cron probe at `.github/workflows/cisco-upstream-check.yml` opens an `upstream-drift` issue on archival, license change, or 90-day staleness.
- **Composite action.** Every `uses:` line is SHA-pinned with a `# v1.2.3` comment for human-readable diff review. No JS / no compiled `dist/`.
- **Self-scan.** Pruner scans Pruner on every push (`.github/workflows/self-scan.yml`). A failing self-scan blocks merge.
- **Release integrity.** `release.yml` re-runs the full scan against the tagged ref. Drift between `main` and the tag fails the release.

## Trust model

The composite action runs entirely on GitHub-hosted or self-hosted runners belonging to the consumer. Pruner produces a signed report bundle that consumers verify with `gh attestation verify` against the public-good Sigstore instance and GitHub OIDC. No Coroboros service is in the trust path.

## Disclosure history

None at v0.1.0.
