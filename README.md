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

- [Why now](#why-now)
- [What Pruner is](#what-pruner-is)
- [Why a wrapper, not another scanner](#why-a-wrapper-not-another-scanner)
- [Code inside skills](#code-inside-skills)
- [What Pruner is not](#what-pruner-is-not)
- [Quick start](#quick-start)
- [Compared to](#compared-to)
- [Reports and verification](#reports-and-verification)
- [Coverage](#coverage)
- [Snyk second opinion](#snyk-second-opinion)
- [Vision](#vision)
- [Governance](#governance)
- [License](#license)

## Why now

The agent-skills ecosystem moved from launch (October 2025) to "registry already poisoned at scale" in four months. Snyk's ToxicSkills audit (February 2026) found 36.82 % of 3,984 scanned skills carrying security flaws and 13.4 % critical issues. The ClawHavoc campaign (Antiy CERT, Koi Security, January–February 2026) placed 1,184 malicious skills across the ecosystem with single-IP C2. Cato CTRL weaponised Anthropic's official `slack-gif-creator` skill in December 2025. Minor edits triggered a remote-fetch-and-execute that delivered MedusaLocker — under a single user-consent trust model.

Vendor responsibility lands on the user. Anthropic states explicitly: *"It is the user's responsibility to only use and execute trusted Skills."* Skills.sh runs a server-side audit at install through the CLI. A direct `git clone` bypasses it entirely. Once a skill is installed, drift is not re-scanned. The trust signal needs to live where the audit happens — at source, before publication.

## What Pruner is

A composite GitHub Action that runs at the publisher's CI before a skill release ships. It produces a single trust artefact: `report-v1.json` plus a CycloneDX SBOM and SLSA build provenance. The bundle is signed with public-good [Sigstore](https://www.sigstore.dev/) and GitHub OIDC, and attached to every release tag. Consumers verify with `gh attestation verify`; no Coroboros service sits in the trust path.

Output is deterministic at v0.1. No LLM keys, no telemetry.

## Why a wrapper, not another scanner

[`cisco-ai-defense/skill-scanner`](https://github.com/cisco-ai-defense/skill-scanner) is the OSS reference engine for skill scanning — Apache-2.0, fully local, thirteen-pass static analyser plus bytecode, behavioural dataflow, meta-analyser, optional LLM-as-judge. Rebuilding it costs a year and yields a worse outcome. Pruner pins it as the detection backend and adds the four things it does not surface as discrete signals:

- **agentskills.io frontmatter conformance** (`FC001`–`FC005`) — kebab-case names, description length, custom-fields-under-metadata, the Coroboros house rule against `metadata.version` (skill versioning is repo-tag-driven), and SPDX licence validation.
- **Identity-file write protection** (`PI-IDFILE-001`) — scripts that write to `AGENTS.md`, `MEMORY.md`, `SOUL.md`, `~/.bashrc`, `.cursorrules`, `.claude/settings.json`, `CLAUDE.md`. The ClawHavoc session-persistent backdoor pattern.
- **PEP-723 inline-deps unpinned** (`PI-PEP723-001`), **markdown-image data-exfil** (`PI-MDIMG-001`), **webhook exfil** (`PI-EXFIL-001`), **remote-fetch-and-execute** (`PI-EXFIL-002`), **allowed-tools-vs-script mismatch** (`PI-PERM-001`) — the supply-chain and permissions families documented in the OWASP Agentic Skills Top 10 and the Maloyan / Namiot SoK (arXiv:2601.17548).
- **Unicode codepoint families as named rules** (`PI-UNI-001` Tag block, `PI-UNI-002` variation selectors, `PI-UNI-003` bidi override, `PI-UNI-004` homoglyph instruction tokens, `PI-UNI-005` zero-width clusters) — Cisco catches these internally; Pruner exposes each as a discrete, OWASP-mapped signal that downstream consumers can audit independently.

The novel contribution is the trust artefact, not the scanner. The scanner is intentionally swappable — `docs/why-cisco.md` documents the swap path. The artefact spec (`report-v1` + SBOM + in-toto attestations) is what travels with the skill.

## Code inside skills

Skill repositories ship code under `scripts/` — shell, Python, JS, TS. Static analysis of all of it is delegated to Cisco's subprocess: Python AST, JS / TS, bash pipeline-analyser with taint flow, bytecode disassembly, Office macros, PDF structural. Pruner does not re-implement bandit, ruff, semgrep, or shellcheck.

The Coroboros pack adds patterns Cisco does not surface as discrete rules: codepoint scans, frontmatter validators, PEP-723 metadata checks, identity-file path matching, webhook / pastebin / tunnel signature regexes, remote-fetch-and-execute patterns, and the cross-file allowed-tools-vs-scripts mismatch. The split is deliberate — Cisco's engine is the SAST surface, the Coroboros pack is the skill-specific posture surface.

## What Pruner is not

- **Not a runtime guard.** Pruner runs at the publisher's CI, not inside a loaded agent. For consumer-side runtime auditing, see [`affaan-m/agentshield`](https://github.com/affaan-m/agentshield) (MIT, TypeScript, three-agent Opus pipeline that audits `.claude/` config, MCP servers, and hooks). Anthropic and skills.sh provide the install-time audit hook.
- **Not a live red-team tool.** Probing a deployed agent with adversarial prompts is the job of [NVIDIA garak](https://github.com/NVIDIA/garak), [promptfoo](https://github.com/promptfoo/promptfoo), or [Microsoft PyRIT](https://github.com/Azure/PyRIT). Those tools require a runnable agent endpoint; many skill repos ship none.
- **Not a proprietary cloud-uplinked engine.** Cisco runs fully local; Pruner runs fully offline by default. [`snyk/agent-scan`](https://github.com/snyk/agent-scan) is a strong scanner but requires `SNYK_TOKEN` and uplinks scan content to Snyk cloud — incompatible with air-gapped or regulated workflows. Pruner accepts it as an opt-in second opinion (see [Snyk second opinion](#snyk-second-opinion)).

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
    uses: ob-aion/pruner/.github/workflows/scan.yml@0.2.0
    with:
      fail-on: medium
      skill-pattern: 'skills/*/SKILL.md'
```

Templates for minimal and full integrations live in [`templates/`](./templates/). Consumer integration walkthrough: [`docs/consumer-integration.md`](./docs/consumer-integration.md).

## Compared to

Each tool answers a different question.

| Tool | Form | Where it runs | License | Network |
| --- | --- | --- | --- | --- |
| **Pruner** (this repo) | composite GitHub Action | publisher CI | Apache-2.0 | offline by default |
| [`cisco-ai-defense/skill-scanner`](https://github.com/cisco-ai-defense/skill-scanner) | CLI + reusable workflow | local or CI | Apache-2.0 | offline (LLM keys optional) |
| [`snyk/agent-scan`](https://github.com/snyk/agent-scan) | CLI | local + Snyk cloud | Apache-2.0 | `SNYK_TOKEN` required |
| [`affaan-m/agentshield`](https://github.com/affaan-m/agentshield) | CLI + GitHub Action + plugin | consumer agent setup | MIT | `ANTHROPIC_API_KEY` for deep analysis |
| [skills.sh audit](https://skills.sh/) (Gen ATH × Socket × Snyk) | server-side, via `npx skills add` | install time | mixed (closed + commercial) | required |

Pruner answers *"is this skill safe to ship?"* — and produces a portable, signed answer that travels with the release tag. AgentShield answers *"is this agent setup safe to load?"* The static scanners answer *"what does deep code analysis say about this artefact?"* The skills.sh audit answers *"is this safe to install through the registry CLI?"* — and is bypassed by `git clone`.

## Reports and verification

Every release attaches `pruner-report.zip` to its GitHub release page. Inside: `report-v1.json`, aggregated SARIF, CycloneDX SBOM, OpenSSF Scorecard JSON, in-toto attestations, badge SVG. Verification:

```bash
gh release download <tag> --repo <owner>/<repo> --pattern 'pruner-report.zip'
gh attestation verify pruner-report.zip --owner <owner>
```

Walkthrough: [`docs/verify-a-report.md`](./docs/verify-a-report.md). Schemas at [`schema/`](./schema/) — JSON Schema 2020-12.

## Coverage

Coverage matrix — what Cisco catches × what the Coroboros pack adds × what nothing covers: [`docs/coverage-matrix.md`](./docs/coverage-matrix.md). FP-audit on `anthropics/skills`, `vercel-labs/agent-skills`, and `coroboros/agent-skills`: [`docs/fp-audit.md`](./docs/fp-audit.md). Threat model and disclosure: [`docs/threat-model.md`](./docs/threat-model.md).

## Snyk second opinion

Optional. Set `with-snyk: true` and provide `SNYK_TOKEN`; Snyk findings land in the report's `tools[]` block with `mode: second-opinion, blocking: false`. Without a token the step is silently skipped. Setup walkthrough: [`docs/consumer-integration.md#snyk-second-opinion`](./docs/consumer-integration.md#snyk-second-opinion). Read the network-egress trade-off in [`docs/why-cisco.md#considered-alternatives`](./docs/why-cisco.md#considered-alternatives) before enabling.

## Vision

The trust artefact is the deliverable. The scanner is replaceable. At 1.0: submit `report-v1` and the attestation bundle shape as a candidate spec contribution to the [OpenSSF Working Group on Supply-Chain Integrity](https://openssf.org/community/supply-chain-integrity/). Register Pruner in the Sigstore landscape alongside.

A signed trust artefact at the publisher boundary closes two gaps that runtime guards and install-time audits cannot reach: direct git-clone of a skill repository bypasses any registry-side audit, and once a skill is installed, post-publish drift is never re-scanned.

## Governance

Apache-2.0. Solo maintainer at v0.x; bus factor declared in [`BUS_FACTOR.md`](./BUS_FACTOR.md). Rule-pack and release policy: [`GOVERNANCE.md`](./GOVERNANCE.md). Threat model and disclosure: [`SECURITY.md`](./SECURITY.md). Contributing: [`CONTRIBUTING.md`](./CONTRIBUTING.md).

## License

Apache-2.0. See [`LICENSE`](./LICENSE).
