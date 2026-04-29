<div align="center">

<!-- omit in toc -->
# Pruner

**Variants don't ship. Signal does.**

Coroboros's attestation chain for agent skill repositories.

[![latest](https://img.shields.io/github/v/release/ob-aion/pruner?style=flat-square&label=latest&color=000000)](https://github.com/ob-aion/pruner/releases)
[![self-scan](https://img.shields.io/github/actions/workflow/status/ob-aion/pruner/self-scan.yml?branch=main&style=flat-square&label=self-scan&color=000000)](https://github.com/ob-aion/pruner/actions/workflows/self-scan.yml)
[![branch](https://img.shields.io/badge/branch-experimental-000000?style=flat-square)](https://github.com/ob-aion/pruner)
[![license](https://img.shields.io/badge/license-Apache--2.0-000000?style=flat-square)](https://www.apache.org/licenses/LICENSE-2.0)
[![stars](https://img.shields.io/github/stars/ob-aion/pruner?style=flat-square&label=stars&color=000000)](https://github.com/ob-aion/pruner)
[![skills](https://img.shields.io/badge/skills-000000?style=flat-square&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDE2IDE2IiBmaWxsPSJ3aGl0ZSI+PHBvbHlnb24gcG9pbnRzPSI4LDAgMTAsNiAxNiw4IDEwLDEwIDgsMTYgNiwxMCAwLDggNiw2Ii8+PC9zdmc+)](https://github.com/coroboros/agent-skills)
[![coroboros.com](https://img.shields.io/badge/coroboros.com-000000?style=flat-square&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiLz48cGF0aCBkPSJNMiAxMmgyME0xMiAyYTE1LjMgMTUuMyAwIDAgMSA0IDEwIDE1LjMgMTUuMyAwIDAgMS00IDEwIDE1LjMgMTUuMyAwIDAgMS00LTEwIDE1LjMgMTUuMyAwIDAgMSA0LTEweiIvPjwvc3ZnPg==)](https://coroboros.com)

</div>

`Detection: cisco-ai-skill-scanner. Policy: coroboros. Signature: Sigstore.`

- [What it does](#what-it-does)
- [Quick start](#quick-start)
- [How it works](#how-it-works)
- [Snyk second opinion](#snyk-second-opinion)
- [Coverage](#coverage)
- [Reports and attestation](#reports-and-attestation)
- [Governance](#governance)
- [License](#license)

## What it does

Pruner audits agent skill repositories on the publishing side — before a `SKILL.md` ever reaches a consumer registry — and emits a signed report that travels with the release.

Detection delegates to [`cisco-ai-defense/skill-scanner`](https://github.com/cisco-ai-defense/skill-scanner) (Apache-2.0, fully local, 13-pass static + bytecode + meta-analyzer). On top of that, the Coroboros policy pack adds twelve default-on rules covering documented gaps — the full Unicode-Tag arsenal, PEP-723 inline-deps without pins, identity-file writes, markdown-image data-exfil, and frontmatter conformance for the [agentskills.io](https://agentskills.io/) spec. Every finding maps to OWASP AST01–AST10 and OWASP LLM01–LLM10.

The output is a single `report-v1.json` bundled with SLSA provenance and a CycloneDX SBOM, signed via [`actions/attest-build-provenance`](https://github.com/actions/attest-build-provenance) and [`actions/attest-sbom`](https://github.com/actions/attest-sbom) using public-good Sigstore. Consumers verify with `gh attestation verify` — no Coroboros services in the trust path.

## Quick start

Drop this into `.github/workflows/pruner.yml`:

```yaml
name: Pruner
on:
  pull_request:
  push:
    tags: ['[0-9]+.[0-9]+.[0-9]+']
  schedule:
    - cron: '0 6 * * 1'

permissions:
  contents: read
  security-events: write
  id-token: write
  attestations: write

jobs:
  audit:
    uses: ob-aion/pruner/.github/workflows/reusable-full-scan.yml@0.1.3
    with:
      fail-on: medium
      skill-pattern: 'skills/*/SKILL.md'
```

Templates for minimal and full integrations live in [`templates/`](./templates/). Consumer integration walkthrough: [`docs/consumer-integration.md`](./docs/consumer-integration.md).

## How it works

Three stages, in sequence:

1. **Detection.** The composite action installs a SHA-pinned `cisco-ai-skill-scanner` in deterministic mode (no LLM keys required), runs `gitleaks` for secrets, and `actionlint` for the audited repo's own workflows.
2. **Coroboros policy pack.** Twelve default-on rules — frontmatter conformance (FC001–FC005), Unicode-Tag arsenal (PI-UNI-001..004), supply-chain hygiene (PI-PEP723-001, PI-IDFILE-001, PI-MDIMG-001). Twelve opt-in PD rules for prompt-defense posture on generalist-agent prompt files.
3. **Attestation.** SBOM via `anchore/sbom-action`, build provenance via `actions/attest-build-provenance`, SBOM signing via `actions/attest-sbom`. Output is a single `report-v1.json` plus the signed bundle, attached to the GitHub release.

Architecture deep-dive: [`docs/architecture.md`](./docs/architecture.md). Why Cisco as the detection backend: [`docs/why-cisco.md`](./docs/why-cisco.md).

## Snyk second opinion

Optional. `ob-aion/pruner` accepts `snyk/agent-scan` as a second-opinion runner — set `with-snyk: true` and provide `SNYK_TOKEN`. Findings land in the report's `tools[]` block with `mode: second-opinion, blocking: false`.

Snyk uplinks scan content to its cloud — incompatible with Pruner's air-gap default. Skip for private or regulated content. Without a token, the step is silently skipped; the workflow does not fail. Setup walkthrough: [`docs/consumer-integration.md#snyk-second-opinion`](./docs/consumer-integration.md#snyk-second-opinion).

## Coverage

Honest matrix of what Cisco catches × what the Coroboros pack adds × what nothing covers: [`docs/coverage-matrix.md`](./docs/coverage-matrix.md). FP-audit on three public skill repos: [`docs/fp-audit.md`](./docs/fp-audit.md).

## Reports and attestation

Every release emits `pruner-report.zip` to its GitHub release page, containing `report-v1.json`, the aggregated SARIF, the CycloneDX SBOM, the OpenSSF Scorecard JSON, the in-toto attestation, and the badge SVG. Verification:

```bash
gh attestation verify pruner-report.zip --owner ob-aion
```

Walkthrough: [`docs/verify-a-report.md`](./docs/verify-a-report.md).

## Governance

Apache-2.0. Solo maintainer at v0.1; bus factor declared in [`BUS_FACTOR.md`](./BUS_FACTOR.md). Rule-pack and release policy: [`GOVERNANCE.md`](./GOVERNANCE.md). Threat model and disclosure: [`SECURITY.md`](./SECURITY.md).

## License

Apache-2.0. See [`LICENSE`](./LICENSE).
