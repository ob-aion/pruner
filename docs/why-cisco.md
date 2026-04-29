# Why Cisco

The detection backend is `cisco-ai-defense/skill-scanner`. This document records why, and how to swap it if needed.

## Choice rationale

Pruner's value is the **trust artefact** — a portable signed attestation chain that travels with the skill release and verifies independently. Detection is a commodity: building a fresh 13-pass static analyzer would be a year of work and would launch with no ecosystem trust.

`cisco-ai-defense/skill-scanner` is the right backend at v0.1 because:

| Property | Why it matters |
|---|---|
| **Apache-2.0** | Permissive; we can wrap, fork, and redistribute. |
| **Fully local** | No `SNYK_TOKEN`-style cloud uplink. Pruner's air-gap thesis survives. |
| **Multi-pass** | 13-pass static + bytecode + LLM-as-judge meta + behavioral dataflow + YARA + homoglyph + Office macros. Broader than any single-pass tool. |
| **Meta-analyzer** | Internal FP-reduction stage with documented suppression discipline. |
| **Multi-format** | OpenClaw, OpenAI Codex Skills, Cursor Agent Skills, agentskills.io. Pruner inherits this via the wrap. |
| **Active maintenance** | Latest release `2.0.9` (2026-04-10). Latest main HEAD `f2858cf3bc1be94e9a51ce0bca9c8d87c64364d7` (2026-04-22). Released within 90-day staleness window. |
| **SARIF output** | Composable with GitHub Code Scanning + Pruner's `report-v1.json`. |

## Pin discipline

The pinned engine version is `cisco-ai-skill-scanner==2.0.9`, documented in [`wrapper/CISCO_PIN.md`](../wrapper/CISCO_PIN.md). The pin includes the main-HEAD SHA at pin time for the staleness probe.

Bumps go through Dependabot + CODEOWNERS-required review. Each bump must:

1. Pass the existing test suite unchanged.
2. Pass the `examples/vulnerable-skill` and `examples/benign-skill` smoke tests.
3. Pass the FP-audit regression on the three public corpora (`coroboros/agent-skills`, `anthropics/skills`, `vercel-labs/agent-skills`).
4. Confirm the upstream LICENSE remains Apache-2.0.

## License-drift halt

`scripts/setup-cisco.sh` greps the installed engine's LICENSE for the Apache-2.0 marker:

```bash
grep -E "Apache License|Apache-2\.0|apache\.org/licenses/LICENSE-2\.0" "${CISCO_LICENSE_PATH}" \
    || { echo "Temporal deviation in upstream. Engine license drifted; halt." >&2; exit 1; }
```

A non-match halts the composite action with exit 3 (internal error). The `Temporal deviation` message is the lore-tagged signal.

## Upstream-monitoring cron

`.github/workflows/cisco-upstream-check.yml` runs monthly:

- `gh repo view cisco-ai-defense/skill-scanner --json isArchived,licenseInfo,latestRelease`
- Confirms `isArchived: false`, license SPDX is `Apache-2.0`, latest release is ≤ 90 days old (warn at ≤ 180 stale).
- On failure, opens an issue tagged `upstream-drift`. Triage SLA: 7 days.

## Swap path

Pruner does not replace the Cisco engine reflexively. Triggers for a swap:

1. **License change.** Upstream moves off Apache-2.0. Auto-detected by the license-drift halt.
2. **Archival or hostile fork.** Upstream repo archived or transferred to a hostile owner. Detected by the monthly cron.
3. **CRITICAL CVE without remediation.** A CVE against the engine itself, unpatched > 30 days, with no upstream activity.
4. **Community alignment shift.** OWASP, Anthropic, or the skills ecosystem adopts a different reference scanner that supersedes Cisco. Tracked in `docs/coverage-matrix.md`.

### Swap procedure

1. **Fork.** `gh repo fork cisco-ai-defense/skill-scanner` at the last good SHA. Apache-2.0 allows redistribution; we just need to maintain attribution and avoid trademark uses.
2. **Replace the engine entry in `wrapper/pyproject.toml` and `wrapper/CISCO_PIN.md`.** The wrapper's `cisco_runner.py` invokes the engine via subprocess; the surface is small.
3. **Or substitute with `snyk/agent-scan`.** Apache-2.0 CLI, similar SARIF output. Trade-off: requires `SNYK_TOKEN` and uplinks scan content to Snyk cloud — explicit consumer disclosure required. Document the trade in the README and the report bundle.
4. **Re-run dogfood FP-audit.** Update `docs/fp-audit.md` with new-engine findings classification.
5. **Tag a minor.** Engine swap is breaking for downstream consumers' allowlist patterns; bump minor with deprecation notice.

The Coroboros policy pack runs after the engine and is engine-agnostic. Swapping the detection backend does not require rewriting any of the 24 rules.

## What we did not pick

- **`snyk/agent-scan`.** Apache-2.0 CLI and excellent toxic-flow analysis, but cloud-uplink mandatory (`SNYK_TOKEN`) breaks the air-gap thesis. Available as opt-in second opinion in the composite action when `SNYK_TOKEN` is present (`with-snyk: true`).
- **`vercel-labs/skills` audit.** Three-partner aggregated audit, but install-time placement (server-side, bypassed by direct git clone). Complementary, not an engine choice.
- **Home-grown engine.** Rejected: maintenance tax of a 50+ rule injection corpus, day-1 trust deficit against an unproven scanner, contested differentiation in a space Cisco and Snyk already cover.
