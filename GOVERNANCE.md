**Lead maintainer:** `@ob-aion`. Bus-factor disclosure in [`BUS_FACTOR.md`](./BUS_FACTOR.md). Co-maintainer signal: active `help-wanted: co-maintainer` issue from v0.1.0 — Cisco upstream-monitoring wants more than one set of eyes.

DCO required (`Signed-off-by:` trailer); no CLA.

## Release cadence

- **0.x experimental.** Minor every 2–4 weeks during active development. Patch as needed.
- **1.0+ stable.** Monthly minor, patch as-needed, major ≥ 6 months apart with deprecation notices.
- Every PR merged to `main` ships a tag and a GitHub release. No batching, no un-released commits.

## Versioning

SemVer strict. Tags are bare version numbers (`0.1.0`, `1.2.3`) — no `v` prefix.

## Rule-pack policy

Rules live under `rules/` and conform to [`schema/rule-v1.json`](./schema/rule-v1.json). Each rule:

- Maps to OWASP LLM01–LLM10 (`owasp_ref`) AND OWASP AST01–AST10 (`owasp_ast`), or both `null` with a written reason.
- Cites a primary source in `rationale`.
- Ships positive AND negative fixtures.
- Has at least one unit test under `wrapper/tests/rules/`.

**Adding a rule.** File a `rule-proposal` issue. The proposal includes rationale, fixtures, and an FP measurement against `examples/benign-skill` and ≥3 public skill repos.

**Demoting a rule.** Rules with measured FP rate > 20 % on the canonical benign corpus drop to `status: experimental` and out of the default pack. Community proposes via `false-positive` issue. Maintainer-approved demotion ships in the next minor with a one-version grace period.

## Cisco upstream-monitoring

Pinned engine + monthly health probe + Dependabot bumps with CODEOWNERS review. Pin and bump procedure: [`wrapper/CISCO_PIN.md`](./wrapper/CISCO_PIN.md). Cron: [`.github/workflows/cisco-upstream-check.yml`](./.github/workflows/cisco-upstream-check.yml). On drift the cron opens an `upstream-drift` issue with a 7-day triage SLA.

## Self-scan integrity

Pruner scans Pruner on every push (`.github/workflows/self-scan.yml`). A failing self-scan blocks merge. The release workflow re-runs the full scan against the tagged ref; drift between `main` and the tag fails the release.

## Security disclosure

Private reports at <https://github.com/coroboros/pruner/security/advisories/new>. SLA in [`SECURITY.md`](./SECURITY.md).

## Code of conduct

Be civil; debate the rule, not the proposer. Bad-faith participation gets blocked.
