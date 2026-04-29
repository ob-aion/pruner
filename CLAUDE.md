# Pruner — Contributor Agent Instructions

For agents (Claude Code, Cursor, Copilot, Codex) and humans working in this repo.

## What this is

`coroboros/pruner` ships a composite GitHub Action that audits agent skill repositories on the publishing side and emits a signed attestation. Engine delegated to `cisco-ai-defense/skill-scanner`. Policy pack and attestation chain Coroboros-owned. License Apache-2.0.

## Architecture (one-liner)

`action.yml` (composite, SHA-pinned) → wrapper Python package → Cisco subprocess + Coroboros pack + gitleaks + actionlint → `compose-report` → `report-v1.json` + SARIF + SBOM + SLSA provenance → `actions/attest-*` → release bundle + badge.

Full diagram: [`docs/architecture.md`](./docs/architecture.md). Why Cisco: [`docs/why-cisco.md`](./docs/why-cisco.md).

## Where things live

- `action.yml` — composite action, primary surface
- `wrapper/` — Python package (`pruner-wrapper`), thin orchestrator + Coroboros pack engine
- `rules/` — Coroboros policy pack (12 default-on, 12 opt-in)
- `schema/` — JSON Schema 2020-12 contracts (rule-v1, report-v1, allowlist-v1, policy-v1)
- `scripts/` — bash helpers invoked by the composite action (`setup-cisco.sh` etc.)
- `templates/` — consumer-facing scaffolds (workflow snippets, SECURITY.md template, badge snippets)
- `examples/` — `vulnerable-skill/` and `benign-skill/` reference fixtures + `EXPECTATIONS.md`
- `docs/` — threat model, coverage matrix, FP audit, why-cisco, writing-rules, verify-a-report
- `.github/workflows/` — `self-scan.yml`, `release.yml`, `scorecard.yml`, `cisco-upstream-check.yml`, `reusable-full-scan.yml`

## Non-negotiables

- **Composite action only.** No JS action, no compiled `dist/`. Every `uses:` SHA-pinned with a `# v1.2.3` comment.
- **Wrapper runtime deps** = `pyyaml` + `cisco-ai-skill-scanner` (pipx-pinned) + Python stdlib. Adding a runtime dep requires explicit justification in the commit body. Dev-only deps (pytest, ruff, mypy, jsonschema) live under `[project.optional-dependencies] dev`.
- **No third-party `regex` module.** `unicodedata.category(c) == 'Cf'` covers `\p{Cf}`.
- **No `metadata.version` in skill frontmatter.** Coroboros house rule (FC004). Skill versioning is repo-tag-driven.
- **No emoji** anywhere except `wrapper/src/pruner_wrapper/lore.py` (lore strings — ASCII-safe by default).
- **No gradient, no shadow, no rounded corners** in any SVG or HTML committed here. Coroboros Design Direction.
- **Apache-2.0 LICENSE verbatim.** Never modify the license body.
- **Conventional Commits with scope.** `type(scope): subject`.
- **No paths exposing local user info** in any committed artefact. Repo-relative or `~/` only.
- **Tags are bare SemVer.** `0.1.0`, never `v0.1.0`.

## When adding a Coroboros pack rule

Required, no exceptions:

1. `rationale` citing OWASP LLM/AST refs, primary research, or a named incident.
2. `owasp_ref` (LLM01–LLM10) AND `owasp_ast` (AST01–AST10), or both `null` with a written reason.
3. Positive AND negative fixtures in the YAML.
4. A test file under `wrapper/tests/rules/test_<RULE_ID>.py` — schema-validates the YAML, asserts positive fixtures match, asserts negative fixtures don't.
5. Source-confidence guidance in scope.
6. FP rate measured against `examples/benign-skill` and ≥3 public skill repos before promotion to `status: stable`.

Walkthrough: [`docs/writing-rules.md`](./docs/writing-rules.md). Schema: [`schema/rule-v1.json`](./schema/rule-v1.json).

## Testing protocol

```bash
cd wrapper
pip install -e ".[dev]"
ruff check src tests
mypy src
pytest tests --cov=pruner_wrapper --cov-fail-under=90
```

Action file:

```bash
actionlint action.yml .github/workflows/*.yml
```

Self-scan integrity (Pruner audits Pruner, every push):

```bash
pruner scan . --without-cisco       # zero critical
```

Examples:

```bash
pruner scan examples/vulnerable-skill --without-cisco   # expected findings per EXPECTATIONS.md
pruner scan examples/benign-skill --without-cisco       # zero findings
```

## Cisco upstream discipline

`wrapper/CISCO_PIN.md` records the pinned version + main-HEAD SHA + Apache-2.0 marker grep. Bumps go through Dependabot + CODEOWNERS review. License-drift triggers `Temporal deviation in upstream. Engine license drifted; halt.` and stops the action. Monthly cron (`.github/workflows/cisco-upstream-check.yml`) probes upstream health.

Swap procedure on license change / archival: [`docs/why-cisco.md`](./docs/why-cisco.md).

## What this repo does NOT do

- Runtime monitoring or sandboxing.
- Consumer-side `.claude/` config scanning (AgentShield's territory).
- Standalone semgrep/CodeQL/bandit/ruff steps (Cisco covers).
- LLM-in-the-loop detection by default (Cisco's `--use-llm` is opt-in upstream; Pruner stays deterministic at v0.1).
- Telemetry or phone-home of any kind.
- Garak/promptfoo agent-side red teaming (separate scope, not v0.x).
- Generic SAST.

## Lore vocabulary

Variant = finding. Threshold = severity gate. Prune = reject. Timeline = protected branch. Signal = legitimate output. Loom = attestation chain. Use sparingly; every lore string must also parse as plain English.
