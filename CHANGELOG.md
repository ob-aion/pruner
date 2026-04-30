# Changelog

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
- **Renamed reusable workflow `reusable-full-scan.yml` → `scan.yml`.** Matches the `pruner scan` CLI verb and the production-grade conventions used by Cisco's `scan-skills.yml` and Snyk's `agent-scan`. The old filename remains in-tree as a deprecation alias that delegates to `scan.yml` via `secrets: inherit`; removed in 0.3.0. Templates and `docs/consumer-integration.md` reference the new filename. Migration is one-line: `uses: ob-aion/pruner/.github/workflows/scan.yml@0.2.0`.

### Breaking changes

- The reusable workflow file is now `scan.yml`. The 0.1.x entry-point `reusable-full-scan.yml` keeps working through the 0.2.x line as a thin alias and is removed in 0.3.0.

### Upgrade notes

- 0.1.x consumers: change `uses: ob-aion/pruner/.github/workflows/reusable-full-scan.yml@0.1.x` to `uses: ob-aion/pruner/.github/workflows/scan.yml@0.2.0`. No input changes.

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
