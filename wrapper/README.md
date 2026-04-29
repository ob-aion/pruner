# pruner-wrapper

The Python module behind the `pruner` CLI and the `coroboros/pruner` composite action. Thin orchestrator over the Cisco engine plus the Coroboros policy pack engine.

## Install

End-user (composite action target):

```bash
pipx install pruner-wrapper
```

Developer (this repo):

```bash
python3 -m venv .venv
source .venv/bin/activate
cd wrapper
pip install -e ".[dev]"
```

The Cisco engine is pinned to `cisco-ai-skill-scanner==2.0.9` and is auto-installed as a dependency. See [`CISCO_PIN.md`](./CISCO_PIN.md).

## CLI

```bash
pruner scan <path> \
    [--rules <path>] \
    [--severity-threshold critical|high|medium|low|info] \
    [--format sarif|json|terminal] \
    [--allowlist .pruner-ignore.yml] \
    [--policy .pruner-policy.yml] \
    [--output <path>] \
    [--skill-pattern 'skills/*/SKILL.md'] \
    [--with-cisco | --without-cisco] \
    [--with-snyk | --without-snyk]

pruner compose --inputs <sarif paths> --output <path> [--policy ...] [--allowlist ...]
pruner badge --report <path> --output <path>
pruner gate --report <path> --fail-on critical|high|medium|low|never
```

Exit codes:

| Code | Meaning |
|---|---|
| 0 | No findings at or above threshold |
| 1 | Findings present, threshold not exceeded |
| 2 | Findings exceed `fail-on` threshold |
| 3 | Internal error (invalid rule, missing input, license drift) |

## Runtime deps

- `pyyaml` — frontmatter parsing, rule YAML loading, allowlist + policy parsing.
- `cisco-ai-skill-scanner` — pinned detection backend (subprocess-invoked).
- Python stdlib otherwise — `re`, `unicodedata`, `subprocess`, `json`, `pathlib`, `argparse`, `dataclasses`, `typing`.

The third-party `regex` module is intentionally NOT used. `unicodedata.category(c) == 'Cf'` covers the Unicode category checks; bounded `re.compile` covers the rest.

## Testing

```bash
ruff check src tests
mypy src
pytest tests --cov=pruner_wrapper --cov-fail-under=90
```

## Pattern types

| Type | Module |
|---|---|
| `regex` | `matchers/regex_matcher.py` |
| `absence-regex` | `matchers/absence_regex_matcher.py` |
| `codepoint-range` | `matchers/codepoint_range_matcher.py` |
| `homoglyph-instruction` | `matchers/homoglyph_matcher.py` |
| `frontmatter-validator` | `matchers/frontmatter_validator.py` |
| `pep723-validator` | `matchers/pep723_validator.py` |
