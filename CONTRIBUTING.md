# Contributing

Thanks for considering a contribution. Pruner is small, opinionated, and maintained by a tiny team — the bar for merging is high, but the rules are explicit.

## Quick path

1. Open an issue first using the appropriate template (`rule-proposal`, `false-positive`, `vulnerability`). Drive-by PRs are usually closed.
2. Fork, branch, change, test, sign off.
3. Pull request against `main`.

## Setup

```bash
git clone https://github.com/coroboros/pruner.git
cd pruner
python3 -m venv .venv
source .venv/bin/activate
cd wrapper
pip install -e ".[dev]"
```

The Cisco engine is installed via pipx separately:

```bash
pipx install "cisco-ai-skill-scanner==2.0.9"
```

## Testing

Run before every commit:

```bash
cd wrapper
ruff check src tests
mypy src
pytest tests --cov=pruner_wrapper --cov-fail-under=90
```

Action lint:

```bash
actionlint action.yml .github/workflows/*.yml
```

Self-scan integrity (Pruner audits Pruner):

```bash
pruner scan . --without-cisco
```

Examples:

```bash
pruner scan examples/vulnerable-skill --without-cisco   # expected findings per EXPECTATIONS.md
pruner scan examples/benign-skill --without-cisco       # zero findings
```

## DCO sign-off

Every commit MUST include a `Signed-off-by:` trailer:

```bash
git commit -s -m "feat(rules): add PI-FOO-001 — short description"
```

This certifies you wrote the change or have permission to contribute it under Apache-2.0. Full text: <https://developercertificate.org/>.

## Conventional commits

Format: `type(scope): subject`. Scope is the affected module: `wrapper`, `rules`, `action`, `attest`, `docs`, `repo`. Examples:

- `feat(rules): add PI-FOO-001 detecting bar attack`
- `fix(wrapper): correct codepoint range for variation selectors`
- `docs(coverage): clarify Cisco's Office macro scope`

## Adding a Coroboros pack rule

Required: see [`docs/writing-rules.md`](./docs/writing-rules.md). Briefly:

1. YAML rule under `rules/<category>/<RULE_ID>-<slug>.yml` conforming to [`schema/rule-v1.json`](./schema/rule-v1.json).
2. `rationale` cites OWASP LLM/AST refs or primary research.
3. `owasp_ref` (LLM01–LLM10) AND `owasp_ast` (AST01–AST10).
4. Positive AND negative fixtures.
5. Test file at `wrapper/tests/rules/test_<RULE_ID>.py`.
6. FP measurement on `examples/benign-skill` and ≥3 public skill repos before promotion to `status: stable`.

## Reporting a false positive

Use the `false-positive` issue template. Include:

- The rule ID.
- A minimal reproducer (the SKILL.md or script that fired).
- Why you believe it's a false positive.
- (Optional) A proposed `context_rules` refinement.

## Reporting a vulnerability

See [`SECURITY.md`](./SECURITY.md). Private GitHub Security Advisory only.
