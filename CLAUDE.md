# Pruner

`ob-aion/pruner` ships a composite GitHub Action that audits agent skill repositories on the publishing side and emits a signed attestation. Engine delegated to `cisco-ai-defense/skill-scanner`. Policy pack and attestation chain Coroboros-owned. License Apache-2.0.

## Architecture

`action.yml` (composite, SHA-pinned) → wrapper Python package → Cisco subprocess + Coroboros pack + gitleaks + actionlint → `compose-report` → `report-v1.json` + SARIF + SBOM + SLSA provenance → `actions/attest-*` → release bundle + badge.

Full diagram: [`docs/architecture.md`](./docs/architecture.md). Why Cisco: [`docs/why-cisco.md`](./docs/why-cisco.md). Threat model: [`docs/threat-model.md`](./docs/threat-model.md).

## Where things live

- `action.yml` — composite action, primary surface.
- `wrapper/` — Python package (`pruner-wrapper`), thin orchestrator + Coroboros pack engine.
- `rules/` — Coroboros policy pack (12 default-on, 12 opt-in).
- `schema/` — JSON Schema 2020-12 contracts.
- `scripts/` — bash helpers invoked by the composite action.
- `templates/` — consumer-facing scaffolds.
- `examples/` — `vulnerable-skill/` + `benign-skill/` fixtures with `EXPECTATIONS.md`.
- `docs/` — threat model, coverage matrix, FP audit, writing-rules, verify-a-report, consumer-integration.
- `.github/workflows/` — `self-scan`, `release`, `scorecard`, `cisco-upstream-check`, `scan` (consumer-facing reusable workflow).

## Non-negotiables

- **Composite action only.** No JS action, no compiled `dist/`. Every `uses:` SHA-pinned with a `# v1.2.3` comment.
- **Wrapper runtime deps** = `pyyaml` + `cisco-ai-skill-scanner` (pinned) + Python stdlib. Adding a runtime dep requires explicit justification in the commit body. Dev-only deps under `[project.optional-dependencies] dev`.
- **No third-party `regex` module.** `unicodedata.category(c) == 'Cf'` covers `\p{Cf}`.
- **No `metadata.version` in skill frontmatter.** Coroboros house rule (FC004). Skill versioning is repo-tag-driven.
- **No emoji** anywhere except `wrapper/src/pruner_wrapper/lore.py`.
- **No gradient, no shadow, no rounded corners** in any SVG or HTML committed here. Coroboros Design Direction.
- **Apache-2.0 LICENSE verbatim.** Never modify the license body.
- **Conventional Commits with scope.** `type(scope): subject`.
- **No paths exposing local user info** in any committed artefact. Repo-relative or `~/` only.
- **Tags are bare SemVer.** `0.1.0`, never `v0.1.0`. CHANGELOG section headers may keep the `v` per Coroboros family convention.

## Testing protocol

```bash
cd wrapper
pip install -e ".[dev]"
ruff check src tests
mypy src
pytest tests --cov=pruner_wrapper --cov-fail-under=90
```

Action + workflows:

```bash
actionlint action.yml .github/workflows/*.yml
```

Self-scan + examples:

```bash
pruner scan . --without-cisco                            # self-scan, zero critical expected
pruner scan examples/vulnerable-skill --without-cisco    # findings per EXPECTATIONS.md
pruner scan examples/benign-skill --without-cisco        # zero findings expected
```

## Authoring rules + upstream discipline

- New Coroboros pack rule → [`docs/writing-rules.md`](./docs/writing-rules.md). Schema at [`schema/rule-v1.json`](./schema/rule-v1.json).
- Cisco engine bumps → [`wrapper/CISCO_PIN.md`](./wrapper/CISCO_PIN.md). License-drift halts the action with `Temporal deviation in upstream. Engine license drifted; halt.`
- Release flow → [`GOVERNANCE.md`](./GOVERNANCE.md#release-cadence) and [`CONTRIBUTING.md`](./CONTRIBUTING.md#changelog-and-releases).

## Anti-scope

Out of scope by decision:

- runtime monitoring
- consumer-side `.claude/` config + MCP server + hook auditing — that is [`affaan-m/agentshield`](https://github.com/affaan-m/agentshield)'s territory (MIT, TypeScript, three-agent Opus 4.6 pipeline, requires `ANTHROPIC_API_KEY`)
- standalone semgrep / CodeQL / bandit / ruff / shellcheck — Cisco's subprocess covers all code SAST
- LLM-in-the-loop detection by default — Pruner is deterministic at v0.x
- telemetry of any kind
- garak / promptfoo / Microsoft PyRIT agent-side red teaming — separate scope, not v0.x; those tools need a runnable agent endpoint
- generic SAST

Full out-of-scope list: [`docs/threat-model.md#out-of-scope`](./docs/threat-model.md#out-of-scope).

## Lore vocabulary

Variant = finding. Threshold = severity gate. Prune = reject. Timeline = protected branch. Signal = legitimate output. Loom = attestation chain. Use sparingly; every lore string must also parse as plain English.
