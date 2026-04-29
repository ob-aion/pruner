# Governance

## Maintainers

- **Lead maintainer:** OB (`@ob-aion`).
- **Co-maintainer signal:** active `help-wanted: co-maintainer` issue from v0.1.0. Cisco upstream-monitoring needs more than one set of eyes.

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

- **Pinned engine.** `wrapper/CISCO_PIN.md` records the pinned version, main-HEAD SHA, and Apache-2.0 marker grep at install time.
- **Monthly probe.** `.github/workflows/cisco-upstream-check.yml` confirms the upstream repo is not archived, the latest release is ≤ 90 days old, the LICENSE remains Apache-2.0, and no critical CVE is open against the engine. Failure opens an `upstream-drift` issue. Triage SLA: 7 days.
- **Bumps.** Dependabot proposes pin updates. CODEOWNERS-required review for changes to `wrapper/CISCO_PIN.md`.

## Self-scan integrity

Pruner scans Pruner on every push (`.github/workflows/self-scan.yml`). A failing self-scan blocks merge. The release workflow re-runs the full scan against the tagged ref; drift between `main` and the tag fails the release.

## Security disclosure

Private reports at <https://github.com/coroboros/pruner/security/advisories/new>. SLA in [`SECURITY.md`](./SECURITY.md).

## Code of conduct

Be civil; debate the rule, not the proposer. Bad-faith participation gets blocked.
