# False-positive audit

Living document. Every release appends a dated section classifying any new findings against the canonical dogfood corpus.

## 0.2.6 — 2026-05-11 (Cisco bump audit)

Triggered by the Cisco engine bump `2.0.9 → 2.0.11`. Cisco `2.0.10` expanded the rule pack from 34 to 314 signatures (~10×). The audit confirms the bump introduces zero net detection drift on the canonical corpus.

### Run metadata

| Field | Value |
|---|---|
| Date | 2026-05-11 |
| Pruner version | 0.2.6 |
| Wrapper engine | `pruner-wrapper` 0.2.6 |
| Cisco engine | `cisco-ai-skill-scanner` 2.0.11 |
| Mode | `--without-cisco --rules rules/` (deterministic Coroboros pack only — same as 0.1.0 baseline) |
| Threshold | `info` (every finding surfaced, none filtered out) |

### Targets

| Repo | HEAD SHA | Tracked files | Skill count | Δ skills vs 0.1.0 |
|---|---|---|---|---|
| `coroboros/agent-skills` | `ce19326ed0cec9ed25900fb21f49e581ae6b8f07` | 307 | 17 | +1 |
| `anthropics/skills` | `f458cee31a7577a47ba0c9a101976fa599385174` | 393 | 18 | 0 |
| `vercel-labs/agent-skills` | `b9c8ee0643d87d3c5a953d1e22382ff2ead39229` | 168 | 7 | 0 |

### Aggregate

| Classification | Count | Δ vs 0.1.0 |
|---|---|---|
| true-positive | 24 | +1 (new coroboros skill matches the FC003 pattern documented at 0.1.0) |
| severity-inflation | 15 | 0 |
| duplicate | 4 | 0 |
| new-rule | 1 | +1 (PI-PERM-001 on `skills/design-system/SKILL.md` — rule added in 0.2.0, true positive) |
| false-positive | 0 | 0 |
| **Total** | **44** | **+2** |

Both deltas trace to corpus and rule-pack evolution since 0.1.0, not to the Cisco bump. **Zero hard FPs preserved.**

### Per-repo

- **`coroboros/agent-skills` — 22 findings (was 20).** FC003 hits go from 16 to 17; the new entry `skills/agent-creator/SKILL.md` carries the same non-canonical top-level keys as the existing 16, and `skills/scaffold` still contributes the FC001/FC002/FC004/FC005 duplicate cluster from a YAML parse failure. PI-PERM-001 fires once on `skills/design-system/SKILL.md`: the skill ships executable scripts (`scripts/audit-extensions.sh`) but `allowed-tools` does not declare `Bash`. True positive against the v0.2.0 cross-file matcher.
- **`anthropics/skills` — 15 findings (unchanged).** Same FC005 ×15 cluster on `Commercial` / `Proprietary` license values. Severity-inflation, intentional non-SPDX surface. **Tracking note 2** (0.1.0) still applies.
- **`vercel-labs/agent-skills` — 7 findings (unchanged).** Same FC004 ×7 hits — Vercel-convention `metadata.version`. **Tracking note 3** (0.1.0) still applies.

### Cisco-bump parity check (out-of-table validation)

Independently of the FP-audit table, both Cisco versions were run with `--with-cisco` on `coroboros-agent-skills` and `vercel-labs-agent-skills` to confirm the rule-pack expansion does not change detection behaviour on the corpora:

| Corpus | Cisco 2.0.9 findings | Cisco 2.0.11 findings | Δ |
|---|---|---|---|
| `coroboros/agent-skills` | 22 (6 rule IDs: `ALLOWED_TOOLS_*_VIOLATION` ×18, `RESOURCE_ABUSE_INFINITE_LOOP` ×4) | 22 (same distribution) | **0** |
| `vercel-labs/agent-skills` | 20 (8 rule IDs: `UNANALYZABLE_BINARY`, `BINARY_FILE_DETECTED`, `MANIFEST_MISSING_LICENSE`, `HIDDEN_DATA_FILE`, `HIDDEN_EXECUTABLE_SCRIPT`, `ARCHIVE_CONTAINS_EXECUTABLE`, `LOW_ANALYZABILITY`, `ARCHIVE_FILE_DETECTED`) | 20 (same distribution) | **0** |

The 280 newly added Cisco rules do not fire on these corpora. Likely target patterns (advanced injection variants, ATR signatures) not present in well-formed skill repositories.

### Open tracking notes (≤ 3 unresolved at release)

Carried forward from 0.1.0 — no resolutions yet:

1. **`coroboros/agent-skills` FC003 cluster.** Now 17 skills with non-canonical top-level frontmatter keys. Tracking; PR upstream pending.
2. **FC005 vs. proprietary-license strings.** Anthropics non-SPDX licenses. No code change at 0.2.6.
3. **`vercel-labs/agent-skills` `metadata.version` convention divergence.** Recommend `.pruner-policy.yml` opt-out for Vercel-pattern consumers. No code change at 0.2.6.

Three notes total. Within the ≤ 3 cap defined in [`GOVERNANCE.md`](../GOVERNANCE.md#rule-pack-policy).

### Reproduction

```bash
mkdir -p /tmp/pruner-dogfood
git -C /tmp/pruner-dogfood clone --depth 1 https://github.com/coroboros/agent-skills.git coroboros-agent-skills
git -C /tmp/pruner-dogfood clone --depth 1 https://github.com/anthropics/skills.git anthropics-skills
git -C /tmp/pruner-dogfood clone --depth 1 https://github.com/vercel-labs/agent-skills.git vercel-labs-agent-skills

for d in coroboros-agent-skills anthropics-skills vercel-labs-agent-skills; do
    pruner scan "/tmp/pruner-dogfood/$d" \
        --without-cisco \
        --rules rules/ \
        --severity-threshold info \
        --format json \
        --output "/tmp/pruner-dogfood/$d.report.json"
done
```

For the Cisco-bump parity check, repeat with `--with-cisco` on each corpus once with the previous binary on PATH (`PATH=$(pipx environment --value PIPX_LOCAL_VENVS)/cisco-ai-skill-scanner-prev/bin:$PATH`) and once with the new binary, then `diff` the rule-id histograms.

### Next audit

`0.3.0` re-runs this corpus when the next Cisco bump or significant Coroboros pack expansion lands. Tracking notes carry forward until they resolve upstream or fold into the rules themselves.

## 0.1.0 — 2026-04-29 (initial audit)

### Run metadata

| Field | Value |
|---|---|
| Date | 2026-04-29 |
| Pruner version | 0.1.0 |
| Wrapper engine | `pruner-wrapper` 0.1.0 |
| Cisco engine | `cisco-ai-skill-scanner` 2.0.9 (skipped at audit time — air-gap mode) |
| Mode | `--without-cisco --rules rules/` (deterministic Coroboros pack only) |
| Threshold | `info` (every finding surfaced, none filtered out) |

### Targets

| Repo | HEAD SHA | Tracked files | Skill count |
|---|---|---|---|
| `coroboros/agent-skills` | `c323a33dd45c896ac9f03df1e0f991734b0390b0` | 255 | 16 |
| `anthropics/skills` | `5128e1865d670f5d6c9cef000e6dfc4e951fb5b9` | 390 | 18 |
| `vercel-labs/agent-skills` | `ce3e64e468f8fa09a2d075d102771838061fdac0` | 168 | 7 |

### Aggregate

| Classification | Count |
|---|---|
| true-positive | 23 |
| severity-inflation | 15 |
| duplicate | 4 |
| false-positive | 0 |
| **Total** | **42** |

Zero hard FPs. The fifteen severity-inflation findings are FC005 license-non-SPDX hits on Anthropic skills that declare commercial / proprietary licenses (`Commercial`, `Proprietary`) — the rule fires correctly per spec, but the Anthropic licensing convention is not OSS-SPDX and the surface is intentional. The findings stay at `low` (the rule severity); inflated relative to their security signal, not a defect to fix.

### `coroboros/agent-skills` — 20 findings

| ID | Path | Class | Resolution |
|---|---|---|---|
| FC001 | `skills/scaffold/SKILL.md` | duplicate | Root cause: malformed YAML frontmatter on this skill. Single fix removes 5 hits across FC001/FC002/FC003/FC004/FC005. |
| FC002 | `skills/scaffold/SKILL.md` | duplicate | (same root cause) |
| FC004 | `skills/scaffold/SKILL.md` | duplicate | (same root cause) |
| FC005 | `skills/scaffold/SKILL.md` | duplicate | (same root cause) |
| FC003 × 16 | various skills | true-positive | The skill repo declares custom frontmatter top-level keys (`category`, `tags`) that should live under `metadata:`. Action: open a PR on `coroboros/agent-skills` to relocate them. |
| FC001 | `skills/scaffold/SKILL.md` (real, not parse-derived) | true-positive | YAML parse error on the file is the underlying issue; once parsing succeeds the FC001 surface re-evaluates. Tracking note 1. |

### `anthropics/skills` — 15 findings

| ID | Path | Class | Resolution |
|---|---|---|---|
| FC005 × 15 | various skills | severity-inflation | License values `"Commercial"` / `"Proprietary"` are intentional non-SPDX tags reflecting Anthropic's commercial-skill convention. The rule fires per spec, but the threat model doesn't apply to non-OSS skills. **Tracking note 2** — defer recommendation to extend `is_valid_spdx` with a short list of well-known proprietary-license strings; no code change at 0.1.0. Allowlist on the consumer side is the supported path. |

### `vercel-labs/agent-skills` — 7 findings

| ID | Path | Class | Resolution |
|---|---|---|---|
| FC004 × 7 | `skills/deploy-to-vercel/SKILL.md`, `skills/web-design-guidelines/SKILL.md`, `skills/vercel-cli-with-tokens/SKILL.md`, `skills/composition-patterns/SKILL.md`, `skills/react-best-practices/SKILL.md`, `skills/react-view-transitions/SKILL.md`, `skills/react-native-skills/SKILL.md` | true-positive (against Coroboros house rule) | Vercel's frontmatter convention legitimately declares `metadata.version`. Coroboros's house rule (FC004) forbids it. **Tracking note 3** — document upstream that Vercel skills are "Vercel-conventional, not Coroboros-conventional" and consumers can disable FC004 via `.pruner-policy.yml` if they adopt Vercel's pattern. |

### Refinements applied at audit time

1. **FC001 forbid_tokens** — removed `claude` from the list. Pre-audit, FC001 fired on `skills/claude-md/SKILL.md` (coroboros) and `skills/claude-api/SKILL.md` (anthropics) — both legitimate names referencing *working with* Claude rather than impersonating Anthropic. The forbid list now covers PUBLISHER identities (`anthropic`, `openai`, `cisco`, `snyk`) only. Resolved at audit time; FC001 fixtures + tests updated.

### Open tracking notes (≤ 3 unresolved at release)

1. **`coroboros/agent-skills` FC003 cluster.** Sixteen skills have non-canonical top-level frontmatter keys. Tracking; PR upstream after `0.1.0` ships.
2. **FC005 vs. proprietary-license strings.** Consider adding `"Proprietary"` and `"Commercial"` to a parallel "non-OSS-SPDX" set, or relaxing FC005 to severity `info` when the value is a known-proprietary string. No code change at 0.1.0.
3. **`vercel-labs/agent-skills` `metadata.version` convention divergence.** Document that Coroboros's FC004 represents a house rule that Vercel-ecosystem skills do not share. Recommend `.pruner-policy.yml` opt-out for Vercel-pattern consumers.

Three notes total. Within the ≤ 3 cap defined in [`GOVERNANCE.md`](../GOVERNANCE.md#rule-pack-policy).

### Reproduction

```bash
mkdir -p /tmp/pruner-dogfood
git -C /tmp/pruner-dogfood clone --depth 1 https://github.com/coroboros/agent-skills.git
git -C /tmp/pruner-dogfood clone --depth 1 https://github.com/anthropics/skills.git anthropics-skills
git -C /tmp/pruner-dogfood clone --depth 1 https://github.com/vercel-labs/agent-skills.git vercel-labs-agent-skills

for d in coroboros-agent-skills anthropics-skills vercel-labs-agent-skills; do
    pruner scan "/tmp/pruner-dogfood/$d" \
        --without-cisco \
        --rules rules/ \
        --format json \
        --output "/tmp/pruner-dogfood/$d.report.json"
done
```

### Next audit

`0.2.0` will re-run this corpus. Cisco engine integration (currently delegated to the composite action's `cisco-run` step) is expected to add detection coverage but should not change the Coroboros pack's classification on these targets.
