# Changelog

## v0.2.11 - 11/05/2026

Copyright-line alignment across the Coroboros workspace. The Pruner `LICENSE` carried the standard Apache-2.0 appendix copyright `Copyright 2026 Coroboros`, missing the `–End of Time` signature already in place on `coroboros/archivist`, `coroboros/agent-skills`, `coroboros/www`. This release adds the signature to the appendix only. Apache-2.0 operative terms (sections 1–9, lines 1–177) are untouched. SPDX classification stays `Apache-2.0` and downstream license scanners read the same boilerplate.

- **`LICENSE` — appendix copyright line: `Copyright 2026 Coroboros` → `Copyright 2026–End of Time Coroboros`.** Single-line edit at line 190 inside the customary `APPENDIX: How to apply the Apache License to your work.` block. No change to grant terms, redistribution conditions, patent grant, trademark clause, or warranty disclaimer.
- **`.github/workflows/scan.yml` — synced to `ob-aion/pruner@0.2.11`** per the lockstep contract.

## v0.2.10 - 11/05/2026

Brand alignment with the other Coroboros subprojects. The Pruner repo shipped without an `assets/` folder at bootstrap (0.1.0) and the README opened on the title block with no Coroboros mark — a gap against `coroboros/archivist` and `coroboros/agent-skills` which both lead with the gold ouroboros at 288×288.

- **Added `assets/logo.png`** — copy of the canonical Coroboros mark used by `coroboros/archivist`, sourced from the shared Coroboros brand asset pool. 660×660 source PNG, 8-bit RGBA, ~84 kB.
- **`README.md` opens on the logo.** `<img src="assets/logo.png" width="288" height="288" alt="Coroboros"/>` inserted inside the existing `<div align="center">` block, immediately above the `# Pruner` title. Matches the archivist README structure line-for-line for visual consistency in side-by-side browsing.
- **`.github/workflows/scan.yml` synced to `ob-aion/pruner@0.2.10`** per the lockstep contract.

## v0.2.9 - 11/05/2026

Composite action now uploads every SARIF artefact in the report bundle to GitHub Code Scanning, not just the Coroboros pack. The Phase β consumer integration surfaced the gap: 22 Cisco engine findings on `coroboros/agent-skills` lived in the workflow artefact bundle but never reached the Security tab, halving the visible signal for any consumer reviewing scan output through GitHub's first-party UI.

- **`action.yml` — `upload-sarif` step targets the report directory.** `sarif_file` now points to `${{ inputs.report-output }}` rather than a single file path. `github/codeql-action/upload-sarif@v4.35.3` walks the directory, picks up every `*.sarif` and `*.sarif.json`, and uploads each under its own tool category. Captures `coroboros.sarif` (pack), `cisco.sarif` (Cisco engine, the 280-rule expansion since 0.2.6), `gitleaks.sarif` (secrets), and `snyk.sarif` when opted in. The `actionlint.json` file ends in `.json` rather than `.sarif.json` and is silently skipped — actionlint findings stay in the bundle for download but do not surface in the Security tab. Three Code Scanning categories appear on a default Pruner run; four when `with-snyk: true` and the secret is set.
- **`.github/workflows/scan.yml` — synced to `ob-aion/pruner@0.2.9`** per the lockstep contract restored in 0.2.7.

## v0.2.8 - 11/05/2026

Bug fix on the composite action's pack-run step: `pruner scan` exits 1 by design when findings exist (informational signal, default `--fail-on=never`), but the `coroboros-pack-run` step propagated that exit code as a workflow failure. Consumers calling `scan.yml@0.2.7` against a repository with at least one skill finding hit the failure on the first PR. The bug stayed hidden across 0.1.0 to 0.2.7 because Pruner's own self-scan runs against a target with zero `SKILL.md` files — exit code stays at 0.

- **`action.yml` — `coroboros-pack-run` masks `pruner scan` exit 1.** Same pattern as the `gate` step at the bottom of the action: `set -uo pipefail` (no `-e`), `|| EXIT=$?`, then `if [ "${EXIT}" -gt 1 ]; then exit "${EXIT}"; fi`. Exit 0 (no findings) and exit 1 (findings below threshold) thread through; exit 2 (above threshold) and exit 3 (internal error) still fail the workflow. Gating remains in the dedicated `gate` step.
- **`action.yml` — Cisco fallback SARIF reflects the current pin.** The dummy SARIF written when `skill-scanner scan-all` produces no output now reports `version: "2.0.11"` to match `wrapper/CISCO_PIN.md`. Cosmetic; affects only the metadata block.
- **`.github/workflows/scan.yml` — synced to `ob-aion/pruner@0.2.8`** per the lockstep contract reinstated in 0.2.7.

## v0.2.7 - 11/05/2026

Catch-up release that syncs the `scan.yml` reusable workflow with the composite-action tag. The 0.2.3, 0.2.4, 0.2.5, and 0.2.6 releases left `.github/workflows/scan.yml:52` pinned to `ob-aion/pruner@0.2.2` — a documented bump step from 0.2.0 onwards that fell through over four consecutive releases. Consumers calling `uses: ob-aion/pruner/.github/workflows/scan.yml@0.2.6` were therefore running the 0.2.2 composite action internally, missing the Cisco engine bump (2.0.9 → 2.0.11) that 0.2.6 shipped.

- **`.github/workflows/scan.yml` now references `ob-aion/pruner@0.2.7`.** The reusable workflow's `uses:` line moves in lockstep with the tag from this release forward. Consumers pinning `scan.yml@0.2.7` get the 0.2.7 composite action which embeds `cisco-ai-skill-scanner==2.0.11`, the v4.35.3 CodeQL upload-sarif action, and every other surface shipped in 0.2.3-0.2.6.

## v0.2.6 - 11/05/2026

Cisco engine bump — first since 0.1.0. Replaces Dependabot PR #10 with the full `wrapper/CISCO_PIN.md` bump procedure (FP-audit corpus run, doc updates, dual-version parity check).

- **`cisco-ai-skill-scanner` pinned to `2.0.11` (was `2.0.9`).** The bump folds in `2.0.10`'s rule-pack expansion from 34 to 314 signatures (~10×, restructured by category) and `2.0.11`'s internal release-pipeline fix. Touched: `wrapper/pyproject.toml`, `wrapper/src/pruner_wrapper/cisco_runner.py` (`PINNED_VERSION`), `scripts/setup-cisco.sh` (default), `wrapper/CISCO_PIN.md` (version, release date, main-HEAD SHA `ff708ea00fd401640112c138711c5c36ff4992a0`, license re-verified at `2026-05-11`), `wrapper/README.md`, and five wrapper test fixtures. `2.0.10`'s opt-in surface (OpenAI-compatible LLM endpoints, LiteLLM Gemini fallback, `--render-markdown` CLI flag) does not affect Pruner — the wrapper stays deterministic at v0.x and never invokes the LLM-as-judge path.
- **`docs/fp-audit.md` 0.2.6 audit section.** Full reproduction against the canonical corpus (`coroboros/agent-skills`, `anthropics/skills`, `vercel-labs/agent-skills`) in both `--without-cisco` (Coroboros pack baseline) and dual-version `--with-cisco` parity check. Result: **zero net Cisco detection drift** on either corpus (22 findings on coroboros, 20 on vercel-labs, identical rule-id distribution between Cisco 2.0.9 and 2.0.11). The 280 newly added Cisco signatures do not fire on well-formed skills — likely target patterns not present in the dogfood targets. Coroboros pack delta vs 0.1.0: +1 FC003 (corpus added one new skill matching the existing non-canonical-frontmatter pattern) and +1 PI-PERM-001 (rule added in 0.2.0, true positive on `coroboros/agent-skills/skills/design-system/SKILL.md`). Three 0.1.0 tracking notes still apply unchanged.
- **License-drift guard re-validated.** `cisco-ai-skill-scanner` 2.0.11 ships Apache-2.0 LICENSE intact at `<venv>/lib/python*/site-packages/cisco_ai_skill_scanner-2.0.11.dist-info/licenses/LICENSE`. `scripts/setup-cisco.sh` greps the Apache marker and halts the composite action with the lore-tagged drift message on any future regression.

## v0.2.5 - 11/05/2026

CI dependency bump prompted by the Node.js 20 deprecation warning surfaced on every release run since 0.2.3.

- **`github/codeql-action/upload-sarif` bumped from `3.35.2` to `4.35.3`.** Affects `.github/workflows/scorecard.yml` and `action.yml`. The v4 line runs on Node.js 24 (v3 is Node.js 20, slated for forced migration on 2026-06-02 and removal on 2026-09-16) and adds OIDC support for Cloudsmith / GCP private registries plus several bundle and bug fixes. No behaviour change for the SARIF-upload-only use case. New SHA pin `e46ed2cbd01164d986452f91f178727624ae40d7` confirmed as a real commit (not a tag object) by `scripts/verify-action-pins.sh`. Replaces Dependabot PR #11 — Dependabot left the `# v3` annotation on the SHA-bumped line; the proper `# v4.35.3` annotation matches the specificity of the rest of the repo's pin comments.

## v0.2.4 - 11/05/2026

Fix to make the 0.2.3 backfill workflow runnable on the cosign 2.5+ release line.

- **`backfill-signatures.yml` switches to the cosign 2.5+ bundle format.** cosign 2.5 made `--bundle` mandatory and silently ignored the legacy `--output-signature` / `--output-certificate` flags, failing the workflow at `create bundle file: open : no such file or directory` on every dispatch against `0.1.3`, `0.2.0`, `0.2.1`. The fix produces a single `pruner-report.zip.sigstore` Sigstore Protobuf Bundle — signature plus Fulcio cert plus Rekor inclusion proof in one file. OpenSSF Scorecard's `releasesAreSigned` probe matches `.sigstore` in its `signatureExtensions` list at v5.3.0, so the Signed-Releases lift is identical to what the original `.sig` path intended.
- **`docs/verify-a-report.md` updated to match.** `cosign verify-blob --bundle <…>.sigstore --new-bundle-format <…>` replaces the prior `--signature` plus `--certificate` flow. One asset to download, one cosign flag set.

## v0.2.3 - 11/05/2026

Retroactive Signed-Releases lift for pre-0.2.2 releases. Ships the tooling; the backfill itself runs manually post-merge.

- **Added `.github/workflows/backfill-signatures.yml`.** A `workflow_dispatch`-only workflow that downloads `pruner-report.zip` from a named release, signs the bytes with cosign keyless (Fulcio OIDC + Rekor transparency log), and uploads `pruner-report.zip.sig` + `pruner-report.zip.pem` companions back to the release. OpenSSF Scorecard's Signed-Releases check samples the last five releases and recognises `.sig`/`.asc`/`.minisig`/`.sign`/`.intoto.jsonl` extensions; pre-0.2.2 releases shipped none of these, so the cumulative ratio kept Signed-Releases at 2/10 even after 0.2.2's in-toto bundles. The backfill adds the missing signature extensions without modifying or re-publishing the original `pruner-report.zip` bytes.
- **`docs/verify-a-report.md` documents the two signature classes.** In-toto build provenance for 0.2.2+ (attests origin + builder + commit, verifiable via `gh attestation verify`) and detached cosign signatures for backfilled pre-0.2.2 releases (attests bytes only, retroactive, verifiable via `cosign verify-blob`). Both anchor to public-good Sigstore; the Rekor entry timestamps the backfill, not the original release.
- **Operator runbook.** Once this PR merges and 0.2.3 is tagged, run `gh workflow run backfill-signatures.yml -f tag=0.1.3` (and `0.2.0`, `0.2.1`) from the default branch. With four cosign-signed pre-0.2.2 assets plus the 0.2.2 and 0.2.3 in-toto bundles, the last-five-releases sample reaches 5/5 signed — Signed-Releases lifts to 10/10 on the next Scorecard cron.

## v0.2.2 - 30/04/2026

Lifts the third remaining Scorecard finding from the 0.2.1 baseline: Signed-Releases.

- **`release.yml` attaches the in-toto attestation bundles as release assets.** `actions/attest-build-provenance` and `actions/attest-sbom` already produced sigstore bundles signed against public-good Sigstore and GitHub OIDC; the bundles were stored in GitHub's attestation API and verifiable via `gh attestation verify`, but the OpenSSF Scorecard webapp inspects asset filenames for `.sig`, `.asc`, or `.intoto.jsonl` extensions and missed them — Signed-Releases scored 0/10 from 0.1.3 through 0.2.1. The new "Stage attestation bundles for release" step copies each `bundle-path` output into `./.pruner/pruner-report.intoto.jsonl` and `./.pruner/pruner-sbom.intoto.jsonl`, then attaches both alongside the existing five release assets. `gh attestation verify` continues to work unchanged — the GitHub-side attestation store is the same; the new files are local copies of the same sigstore bundles, exposed under filenames the heuristic recognises.

## v0.2.1 - 30/04/2026

Post-release housekeeping. Lifts two findings on the OpenSSF Scorecard baseline.

- **Dropped `pip install --quiet --upgrade pip`** from `scripts/setup-cisco.sh`. `actions/setup-python` already provides a recent pip; the explicit upgrade was a redundant `pipCommand` finding for Scorecard's Pinned-Dependencies check.
- **Added a `SCORECARD_TOKEN` fallback** to `.github/workflows/scorecard.yml`: `repo_token: ${{ secrets.SCORECARD_TOKEN || secrets.GITHUB_TOKEN }}`. The default `GITHUB_TOKEN` cannot read classic branch-protection rules, which scored Branch-Protection at `-1` (inconclusive). Wiring an optional fine-grained PAT (with `Administration: read` scope on the repo, stored as the `SCORECARD_TOKEN` secret) lifts the check to a real score; in the secret's absence the workflow falls back to `GITHUB_TOKEN` and behaves as before.
- **`docs/secrets.md` consolidates token discipline.** Covers `SCORECARD_TOKEN` (maintainer-side) and `SNYK_TOKEN` (consumer-side, opt-in), with the setup walkthrough and the explicit guarantee that verification needs no token. `CONTRIBUTING.md` and `docs/consumer-integration.md` cross-reference it.
- **Doc surface tightened** across `README.md`, `BUS_FACTOR.md`, `SECURITY.md`, `CONTRIBUTING.md`, `GOVERNANCE.md`, `CLAUDE.md`, `rules/README.md`, `wrapper/README.md`, `templates/badge-snippets.md`, and every file under `docs/`. Sentences over the doc word-cap split into shorter forms; section headers and emphasis normalised; contributor-facing prose moved to third-person or imperative. No content claims changed.
- **`rules/README.md` reflects the 0.2.0 reality** — 16 default-on rules (was 12), including the new `permissions/` pillar with `PI-PERM-001`. `tool-grant-validator` added to the pattern-type lists in `docs/writing-rules.md` and `wrapper/README.md`.

## v0.2.0 - 30/04/2026

Pack expansion, attestation guard rails, scan workflow rename.

- **Pinned `ossf/scorecard-action` to commit SHA `4eaacf0543bb3f2c246792bd56e8cdeffafb205a`** (was `99c09fe975337306107572b4fdf4db224cf8e2f2`, the annotated-tag-object SHA). The OpenSSF Scorecard webapp validates that pinned SHAs resolve to real commits and rejects tag objects with a 400 / `imposter commit` error — `0.1.x` was uploading SARIF to Code Scanning correctly but failing the score-publish step.
- **Pinned `github/codeql-action/upload-sarif` to commit SHA `ce64ddcb0d8d890d2df4a9d1c04ff297367dea2a`** (was `865f5f5c36632f18690a3d569fa0a764f2da0c3e`, also a tag-object SHA). Same root cause; affects `scorecard.yml` and `action.yml`.
- **Added `scripts/verify-action-pins.sh`** — pre-flight script that walks every `.github/workflows/*.yml` and `action.yml`, resolves each pinned action SHA against the upstream repository's `commits` API, and fails non-zero on tag-object SHAs. Wired into `release.yml` so a bad pin halts the release before the tag is cut.
- **Documented the tag-object-vs-commit gotcha** in `docs/sha-pinning.md` for future contributors.
- **Added rule `PI-UNI-005-zero-width`** — clusters of three or more zero-width characters (`U+200B-U+200D`, `U+FEFF`) on instruction-bearing text. Same matcher family as `PI-UNI-001/002/003`; the threshold avoids false positives on legitimate ZWJ emoji modifiers and RTL/LTR shaping.
- **Added rule `PI-EXFIL-001-webhook-exfil`** — references to Discord webhooks, Slack incoming webhooks, `paste.ee`, `pastebin.com`, `transfer.sh`, `requestbin.(com\|net)`, `webhook.site`, and `ngrok` tunnels in scripts or `SKILL.md`. Classic exfil channel; observed across the ClawHavoc and MedusaLocker campaigns.
- **Added rule `PI-EXFIL-002-curl-pipe-execute`** — remote-fetch-and-execute patterns (`curl … \| bash`, `wget … \| sh`, `iwr … \| iex`, `eval $(curl …)`, `bash <(curl …)`). The Cato CTRL `slack-gif-creator` weaponization (Dec 2025) used exactly this pattern.
- **Added rule `PI-PERM-001-allowed-tools-mismatch`** — flags a `SKILL.md` whose `allowed-tools` declaration omits `Bash` (or a wildcard equivalent) yet ships `scripts/*.py` that import `subprocess`/`pty` or `scripts/*.sh` containing executable lines. New cross-file matcher type `tool-grant-validator`.
- **Added matcher type `tool-grant-validator`** (`schema/rule-v1.json` enum + `wrapper/src/pruner_wrapper/matchers/tool_grant_validator.py`). Cross-file matchers receive the scan-tree root via the new `pack_runner.get_scan_context()` helper.
- **Extended `examples/vulnerable-skill`** with tripwires for the four new rules and updated `EXPECTATIONS.md` cross-walk. `.pruner-ignore.yml` adds matching allowlist entries with explicit justifications.
- **Schema enrichment** (`schema/rule-v1.json`): three optional taxonomy fields — `mitre_atlas` (array of `AML.T####(.###)?` technique IDs), `nist_ai_rmf` (array of `GV/MP/MS/MG-N(.M)*` subcategory references), `taxonomy_3d` (Maloyan/Namiot SoK 3-D — `delivery` × `modality` × `propagation` enums). Backwards-compatible — unknown keys were already tolerated; existing rules backfill incrementally in 0.2.x. New 0.2.0 rules (PI-UNI-005, PI-EXFIL-001/002, PI-PERM-001) ship populated.
- **Renamed reusable workflow `reusable-full-scan.yml` → `scan.yml`.** Matches the `pruner scan` CLI verb and the production-grade conventions used by Cisco's `scan-skills.yml` and Snyk's `agent-scan`. Templates and `docs/consumer-integration.md` reference the new filename. Consumer line: `uses: ob-aion/pruner/.github/workflows/scan.yml@0.2.0`.
- **Dynamic version derivation via `setuptools-scm`.** `wrapper/pyproject.toml` declares `dynamic = ["version"]`; the package version is read from the git tag at install / build time and written to `wrapper/src/pruner_wrapper/_version.py` (gitignored). `BUS_FACTOR.md`, `SECURITY.md`, and `wrapper/CISCO_PIN.md` no longer carry hardcoded version stamps. `wrapper/tests/test_compose.py` reads `__version__` rather than asserting a literal. Future releases bump exactly two files: `scan.yml`'s `uses: ob-aion/pruner@<X>` line and a fresh `CHANGELOG.md` entry.
- **README rewrite** — the front door now leads with the four-month threat surface (ClawHavoc + ToxicSkills + Cato CTRL MedusaLocker), explains the wrapper rationale (Cisco does the engine work; Pruner adds the trust artefact + Coroboros pack), states the trust-artefact spec vision (`report-v1` + SBOM + in-toto attestations as a candidate OpenSSF WG-Supply-Chain-Integrity contribution at 1.0), and ships a comparison table against `cisco-ai-defense/skill-scanner`, `snyk/agent-scan`, `affaan-m/agentshield`, and the skills.sh install-time audit.
- **AgentShield citation** added to `CLAUDE.md` anti-scope, `docs/threat-model.md` out-of-scope, `docs/coverage-matrix.md` MCP-runtime row. Different trust boundary: Pruner answers *"is this skill safe to ship?"*; AgentShield answers *"is this agent setup safe to load?"*
- **`docs/why-cisco.md`** explicitly documents that Pruner does no independent code SAST. All `sh` / `py` / `js` / `ts` analysis is delegated to Cisco's subprocess (Python AST, JS / TS, bash pipeline-analyser with taint flow, bytecode, Office macros, PDF structural). The Coroboros pack adds only what Cisco does not surface as discrete signals.

## v0.1.3 - 29/04/2026

Patch release fixing the gate-step exit-code interpretation in the composite action and finishing the OpenSSF Scorecard permission-tightening pass.

- **Composite gate step now treats `pruner gate` exit code 1 as pass.** Per the CLI spec, exit 1 means findings exist but none above the configured threshold (informational signal). The composite previously propagated exit 1 as a workflow failure, which made every consumer with non-critical findings see their CI fail unexpectedly. Exit 2 (above threshold) and exit 3 (internal error) still fail the workflow.
- **Workflow permissions tightened** on `self-scan.yml`, `scorecard.yml`, and `cisco-upstream-check.yml`: top-level `contents: read`, write declared at job level only. Mirrors the change `release.yml` shipped in 0.1.1.

0.1.3 is the first release pipeline that actually attaches the signed bundle to the GitHub release page; 0.1.0 / 0.1.1 / 0.1.2 release pages are deleted (tags retained as immutable history).

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
