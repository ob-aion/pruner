# Threat model

Canonical threat model for Pruner. Top-level [`SECURITY.md`](../SECURITY.md) holds the disclosure procedure and SLA; this document describes what Pruner detects, what it ignores, and why.

## Audience

Pruner runs on the **publishing side** of an agent skill repository — the maintainer's CI, before the artefact reaches a registry. The threat model is calibrated for a maintainer who controls the repo but does not control the consumer runtime.

## Asset

The published `SKILL.md` and its referenced files (`scripts/`, `references/`, `assets/`, `.github/workflows/`). The signed report bundle is the trust artefact that travels with the release.

## Adversary

A malicious contributor — or a compromised maintainer account — landing one of the following on `main` or a release tag:

1. **Direct prompt injection** in `SKILL.md` body or frontmatter `description`. Detection: Cisco LLM-judge + deterministic, plus PI-UNI-* for hidden encodings.
2. **Indirect injection** through referenced files (`references/*.md`, fetched URLs at runtime). Detection: Cisco scans every reachable file; Pruner's PI-MDIMG-001 covers the markdown-image exfil class.
3. **Supply-chain poisoning** via `requirements.txt`, `package.json`, PEP-723 inline-deps, typosquatted package names. Detection: Cisco for unpinned deps and typosquatting; Pruner's PI-PEP723-001 for the inline-script class.
4. **Identity-file backdoor** writing to `AGENTS.md` / `MEMORY.md` / `~/.bashrc` / `.cursorrules` / `.claude/settings.json`. Detection: Pruner's PI-IDFILE-001.
5. **Permission abuse** — over-broad `allowed-tools`, hidden `Bash(*)`, `disable-model-invocation: false` with weaponised description. Detection: Cisco.
6. **Hidden encoding** — Unicode Tag block, variation selectors, bidi override (Trojan Source), homoglyphs. Detection: Pruner's PI-UNI-001..004 surface these as discrete signals.
7. **Hostile bundled scripts** — compiled bytecode, base64-shell, `curl … | bash`. Detection: Cisco bytecode + dataflow.
8. **Hostile workflow YAML** in the audited repo's `.github/workflows/`. Detection: actionlint.
9. **Secrets leak** — API keys, SSH keys, tokens. Detection: gitleaks.

## In scope

- Static analysis of `SKILL.md`, frontmatter, `scripts/`, `references/`, `assets/`, and `.github/workflows/` files in the audited repo.
- Detection delegated to `cisco-ai-defense/skill-scanner` (Apache-2.0) under SHA pin, plus the Coroboros policy pack of 12 default-on rules + 12 opt-in PD rules.
- Secrets scanning via `gitleaks`.
- Workflow safety via `actionlint`.
- Attestation via `actions/attest-build-provenance` + `actions/attest-sbom`.

Output is deterministic at v0.1 — no LLM keys required.

## Out of scope

- **Runtime monitoring** of an agent that has already loaded a skill — different trust boundary. See [`affaan-m/agentshield`](https://github.com/affaan-m/agentshield) (MIT, TypeScript, three-agent Opus pipeline) for consumer-side `.claude/` config, MCP server, and hook auditing. Pruner answers *"is this skill safe to ship?"*; AgentShield answers *"is this agent setup safe to load?"*. No overlap, complementary tools.
- **Sandboxed execution** of scanned content — Pruner does not run the scripts it audits.
- **Multimodal injection through fetched URLs** — Pruner flags external URL references in `SKILL.md` but does not fetch them. `vercel-labs/skills` runs the install-time audit (Gen ATH × Socket × Snyk) which is bypassed by direct `git clone` — Pruner's source-side placement closes that gap.
- **Latent semantic activation** — delayed-trigger backdoors that activate after N invocations or specific weekday / locale conditions are not statically visible. Cisco's behavioural pass catches some; the rest need runtime guards.
- **Office macros, polyglot files, encrypted ZIPs** in `assets/` — Cisco covers via YARA; Pruner does not duplicate.
- **Taint / dataflow analysis** — delegated to Cisco's pipeline-analyser.
- **MCP server runtime behaviour** — `snyk/agent-scan` (CLI, requires `SNYK_TOKEN`) and AgentShield (LLM-orchestrated). Pruner does not run agent-side probes.
- **Live agent red-teaming** — out of v0.x scope. Tools that probe a runnable agent: NVIDIA garak, promptfoo, Microsoft PyRIT. Phase-4 reconsideration documented in `brain/research/pruner/NEXT.md` (private roadmap).
- **Image / PDF OCR injection** — Cisco scans some; full multimodal is out of v0.x scope.

Per-rule × per-tool coverage matrix: [`docs/coverage-matrix.md`](./coverage-matrix.md).

## Trust boundaries

Pruner emits a signed bundle that downstream consumers verify with `gh attestation verify`. The verification path uses public-good Sigstore + GitHub OIDC. **No Coroboros service is in the trust path.** A consumer can verify a Pruner report from years past even if Coroboros disappears.

The Cisco engine ships under Apache-2.0 with a SHA-pinned dependency in [`wrapper/CISCO_PIN.md`](../wrapper/CISCO_PIN.md). License-drift halts the action on upstream license change.

## What "Pruner Verified" means

A signed attestation that the audited repo, at the scanned commit:

- Was scanned by `cisco-ai-skill-scanner` at the pinned version with no findings exceeding the consumer's `fail-on` threshold (or with allowlisted findings, listed transparently in the report).
- Passed every default-on Coroboros pack rule (12 rules at v0.1).
- Passed gitleaks and actionlint against the audited surface.
- Has a verifiable SLSA build provenance and a CycloneDX SBOM.

It does NOT mean: the skill is safe to run on arbitrary inputs in arbitrary agents; that the skill is free of latent semantic backdoors; that the skill is compliant with EU AI Act / NIST / SOC 2.

## False-positive discipline

Rules with measured FP rate > 20 % on the canonical benign corpus drop to `status: experimental` and out of the default pack. Per-rule `context_rules` provide in-matcher suppression. Repo-level `.pruner-ignore.yml` requires mandatory justification and is listed in every report. Living audit: [`docs/fp-audit.md`](./fp-audit.md).

## Audit-the-auditor

Pruner's own attack surface is small but real:

- **Wrapper package (`pruner-wrapper`).** Runtime deps are `pyyaml` and `cisco-ai-skill-scanner` (the pinned engine). Stdlib otherwise. The dependency surface is reviewable in `wrapper/pyproject.toml`. Dependabot tracks bumps; CODEOWNERS-required review.
- **Cisco engine.** Apache-2.0, multi-thousand-LOC scanner. Pinned at `2.0.9`. License-drift check runs at install ([`scripts/setup-cisco.sh`](../scripts/setup-cisco.sh)) and halts the action if the upstream license marker changes. Monthly cron probe at [`.github/workflows/cisco-upstream-check.yml`](../.github/workflows/cisco-upstream-check.yml) opens an `upstream-drift` issue on archival, license change, or 90-day staleness.
- **Composite action.** Every `uses:` line is SHA-pinned with a `# v1.2.3` comment for human-readable diff review. No JS / no compiled `dist/`.
- **Self-scan.** Pruner scans Pruner on every push ([`.github/workflows/self-scan.yml`](../.github/workflows/self-scan.yml)). A failing self-scan blocks merge.
- **Release integrity.** [`release.yml`](../.github/workflows/release.yml) re-runs the full scan against the tagged ref. Drift between `main` and the tag fails the release.
