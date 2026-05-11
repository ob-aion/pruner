# Cisco engine pin

Pruner pins the detection backend to a specific `cisco-ai-skill-scanner` release. This file documents the current pin, the verification at install time, and the bump procedure.

## Current pin

| Field | Value |
|---|---|
| Package | `cisco-ai-skill-scanner` |
| Version | `2.0.11` |
| Release date | `2026-04-30` |
| Upstream main HEAD at pin time | `ff708ea00fd401640112c138711c5c36ff4992a0` (`2026-04-30`) |
| License | Apache-2.0 (verified at install via `scripts/setup-cisco.sh`; re-verified 2026-05-11) |
| Upstream | <https://github.com/cisco-ai-defense/skill-scanner> |
| PyPI | <https://pypi.org/project/cisco-ai-skill-scanner/2.0.11/> |
| CLI binaries | `skill-scanner`, `skill-scanner-api`, `skill-scanner-pre-commit` |

## License-drift verification

`scripts/setup-cisco.sh` greps the installed engine's LICENSE for the Apache-2.0 marker. Non-match halts the composite action with exit 3 and the lore-tagged message:

```
Temporal deviation in upstream. Engine license drifted; halt.
```

The installed LICENSE path lives under the pipx venv at:

```
$(pipx environment --value PIPX_LOCAL_VENVS)/cisco-ai-skill-scanner/lib/python*/site-packages/cisco_ai_skill_scanner-*.dist-info/licenses/LICENSE
```

The grep pattern is `Apache License|Apache-2\.0|apache\.org/licenses/LICENSE-2\.0`.

## Health probe

`.github/workflows/cisco-upstream-check.yml` runs monthly:

- Confirms `isArchived: false` on `cisco-ai-defense/skill-scanner`.
- Confirms latest release ≤ 90 days old (warn at ≤ 180).
- Confirms the upstream `LICENSE` still contains the Apache-2.0 marker.
- Confirms no critical CVE is open against the engine on NVD.

Failure opens an issue tagged `upstream-drift`. Triage SLA: 7 days.

## Bump procedure

1. Open a `chore(deps): bump cisco-ai-skill-scanner to <NEW>` PR (Dependabot does this automatically on weekly schedule).
2. Update `wrapper/pyproject.toml` `dependencies` line to the new pin.
3. Update this file: bump version, release date, main-HEAD SHA, license verification status.
4. Re-run the FP-audit corpus locally:
   ```
   pruner scan /tmp/pruner-dogfood/coroboros-agent-skills
   pruner scan /tmp/pruner-dogfood/anthropic-skills
   pruner scan /tmp/pruner-dogfood/vercel-labs-agent-skills
   ```
5. Update `docs/fp-audit.md` with regression notes if findings shift materially.
6. CODEOWNERS-required review.
7. Merge → tag minor → release per [`GOVERNANCE.md`](../GOVERNANCE.md#release-cadence).

## Why this version

`2.0.11` ships everything `2.0.9` shipped, plus:

- **Rule pack expansion 34 → 314** (2.0.10). Restructured by category. The wrapper layer is unaffected because every Cisco rule round-trips as a SARIF result the wrapper composes into `report-v1.json` without per-rule handling.
- **OpenAI-compatible LLM endpoints** and **LiteLLM Gemini fallback** (2.0.10). Both opt-in; Pruner stays deterministic at v0.x and never invokes them.
- **`--render-markdown` override** (2.0.10). Cosmetic CLI flag; Pruner consumes SARIF.
- **Dependency hygiene** (2.0.10): relaxed abstract pins, tightened lockfile, added CI gates. Reduces downstream pip-resolution noise.
- **Release pipeline fix** (2.0.11): assets uploaded before publish (internal Cisco fix; no consumer impact).

Carried forward from `2.0.9`:

- Multi-engine static analyzer (13 passes) with documented meta-analyzer FP reduction.
- Bytecode analyzer for `.pyc` shipped in `scripts/`.
- LLM-as-judge as opt-in (Pruner stays deterministic at v0.x).
- YARA + homoglyph + Office macros + PDF passes.
- SARIF output that composes with Pruner's `report-v1.json` schema.
- Apache-2.0 LICENSE present and valid (re-verified `2026-05-11`).
- No `CRITICAL` open CVE on NVD against the engine at pin time.

## Swap path (license change / archival)

Documented in [`docs/why-cisco.md`](../docs/why-cisco.md). Two routes:

1. Fork upstream at the last good SHA under Apache-2.0; bump the pin to the fork.
2. Substitute `snyk/agent-scan` (Apache-2.0 CLI) — accepts the `SNYK_TOKEN` cloud-uplink trade-off; explicit consumer disclosure required in the report.
