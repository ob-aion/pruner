# Contributing

Thanks for considering a contribution. Pruner is small and solo-maintained. The bar for merging is high; the rules are explicit.

## Quick path

1. Open an issue first using the appropriate template (`rule-proposal`, `false-positive`, `vulnerability`). Drive-by PRs are usually closed.
2. Fork, branch, change, test, sign off.
3. Pull request against `main`.

## Setup

```bash
git clone https://github.com/ob-aion/pruner.git
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

## Repository secrets

Token discipline lives in [`docs/secrets.md`](./docs/secrets.md).

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

Every commit must include a `Signed-off-by:` trailer:

```bash
git commit -s -m "feat(rules): add PI-FOO-001 — short description"
```

The trailer certifies authorship or permission to contribute the change under Apache-2.0. Full text: <https://developercertificate.org/>.

## Conventional commits

Format: `type(scope): subject`. Scope is the affected module: `wrapper`, `rules`, `action`, `attest`, `docs`, `repo`. Examples:

- `feat(rules): add PI-FOO-001 detecting bar attack`
- `fix(wrapper): correct codepoint range for variation selectors`
- `docs(coverage): clarify Cisco's Office macro scope`

## Changelog and releases

[`CHANGELOG.md`](./CHANGELOG.md) is the user-facing release log. Every PR that ships a behaviour change appends a bullet under the next version entry. Format mirrors the rest of the Coroboros family: section header `## vX.Y.Z - DD/MM/YYYY`, terse bullets describing what's in the release.

Versioning is SemVer strict. Git tags and GitHub release titles use the bare version (`0.1.0`, never `v0.1.0`). The CHANGELOG section header is the only place the `v` prefix is used, by presentation convention. One PR maps to one tag and one GitHub release. Release cadence and rule-pack policy live in [`GOVERNANCE.md`](./GOVERNANCE.md).

## Adding a Coroboros pack rule

See [`docs/writing-rules.md`](./docs/writing-rules.md) for the schema, the source-confidence weighting, and the test conventions. Promotion to `status: stable` requires positive + negative fixtures, OWASP LLM/AST refs, and an FP measurement on `examples/benign-skill` plus ≥3 public skill repos.

## Reporting a false positive

Use the `false-positive` issue template. Include:

- The rule ID.
- A minimal reproducer (the SKILL.md or script that fired).
- Why the finding is a false positive.
- (Optional) A proposed `context_rules` refinement.

## Reporting a vulnerability

See [`SECURITY.md`](./SECURITY.md). Private GitHub Security Advisory only.
