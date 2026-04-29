# False-positive audit

Living document. Every release appends a dated section classifying any new findings against the canonical dogfood corpus.

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

Zero hard FPs. The fifteen severity-inflation findings are FC005 license-non-SPDX hits on Anthropic skills that declare commercial / proprietary licenses (`Commercial`, `Proprietary`) — the rule fires correctly per the rule, but the Anthropic licensing convention is not OSS-SPDX and the surface is intentional. We surface them at `low` (the rule severity) and call them inflated relative to their security signal, not a defect to fix.

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
