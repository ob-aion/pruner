# Writing a Coroboros pack rule

Rules live under `rules/<category>/<RULE_ID>-<slug>.yml` and conform to [`schema/rule-v1.json`](../schema/rule-v1.json).

## Anatomy

```yaml
id: PI-FOO-001
slug: foo-attack-detector
title: "Detects the Foo attack pattern"
severity: high
category: prompt-injection                     # one of: prompt-injection, prompt-defense, secrets, permissions, integrity, governance, supply-chain
owasp_ref: LLM01                               # LLM01..LLM10 or null
owasp_ast: AST01                               # AST01..AST10 or null
pattern:
  type: regex                                  # regex | absence-regex | codepoint-range | homoglyph-instruction | frontmatter-validator | pep723-validator | tool-grant-validator
  value: '<pattern body>'
rationale: |
  Free text. Cite OWASP LLM/AST refs and primary research.
references:
  - https://owasp.org/www-project-agentic-skills-top-10/ast01.html
  - https://example.com/primary-source
fixtures:
  positive:
    - "<input that should match>"
  negative:
    - "<input that should NOT match>"
scope:
  file_patterns:
    - "skills/**/SKILL.md"
  ignore_in_fenced_blocks: false
context_rules:
  skip_if_line_starts_with: []
  skip_if_path_matches: []
  skip_if_fenced_block_lang_in: []
weight_override: null                          # null = use source-confidence default; numeric = locked weight
fix:
  auto: false
  description: "Free text describing remediation."
status: stable                                 # stable | experimental | deprecated
since: "0.1.0"
```

## Pattern types

| Type | Use for |
|---|---|
| `regex` | Plain text patterns. Compiled with `re.MULTILINE`. |
| `absence-regex` | Triggers when the pattern is absent. Used by the PD pack (defensive language absent). Combine with `activation_gate`. |
| `codepoint-range` | Ranges of forbidden Unicode codepoints. Used by PI-UNI-001/002/003. |
| `homoglyph-instruction` | Mixed-script lookalikes for instruction tokens. Used by PI-UNI-004. Confusables table is built-in. |
| `frontmatter-validator` | Structural validation of YAML frontmatter. Used by FC001–FC005. Supports `field`+`must_match`, `field`+`min_length`, `field`+`max_length`, `field`+`must_match_spdx`, `field`+`must_be_absent`, `field`+`forbid_tokens`, `field`+`optional`, `forbid_top_level_fields_outside`, `field_path` (dotted). |
| `pep723-validator` | PEP-723 inline-script metadata validation. Used by PI-PEP723-001. Supports `require_pin_operator`. |
| `tool-grant-validator` | Cross-file matcher: SKILL.md frontmatter `allowed-tools` vs sibling `scripts/`. Used by PI-PERM-001. Reads the scan-tree root via `pack_runner.get_scan_context()`. |

New pattern types are additive and require a minor bump of `schema/rule-v1.json`.

## Source confidence

Findings inherit a weight from their file path:

| Tag | Weight | Path patterns |
|---|---|---|
| `active-runtime` | 1.00 | `skills/*/SKILL.md`, anything the agent loads as-is |
| `hook-code` | 1.00 | files referenced from a hook manifest |
| `project-local-optional` | 0.75 | `.pruner.local.yml` and opt-in local overrides |
| `plugin-manifest` | 0.50 | `.claude-plugin/marketplace.json` and siblings |
| `template-example` | 0.25 | `templates/**`, `examples/**`, `samples/**`, `demo/**`, `playground/**` |
| `docs-example` | 0.25 | `docs/**`, `guide/**`, `tutorial/**`, `cookbook/**` |
| `test-fixture` | 0.25 | `tests/**`, `**/fixtures/**`, `**/__snapshots__/**` |

Use `weight_override: 1.00` for invariant signals — invisible payloads don't get diluted just because they sit in `docs/`.

## Context rules — in-matcher FP suppression

`context_rules` suppresses matches at the matcher level, complementary to repo-level `.pruner-ignore.yml`:

```yaml
context_rules:
  skip_if_line_starts_with: ["#", "//", "<!--"]
  skip_if_path_matches: ["docs/threat-examples/**"]
  skip_if_fenced_block_lang_in: ["text", "example", "quote"]
```

## SPDX list (for `must_match_spdx`)

The built-in SPDX identifier list lives in `wrapper/src/pruner_wrapper/spdx.py`. Default coverage: top ~30 OSI-approved identifiers. Expand the list there if a legitimate identifier is missing.

## Confusables table (for `homoglyph-instruction`)

`wrapper/src/pruner_wrapper/confusables.py` ships a small table of Cyrillic/Greek single-character substitutions for the 12 instruction tokens (`ignore`, `system`, `prompt`, `instructions`, `override`, `disregard`, `forget`, `you`, `are`, `now`, `admin`, `root`). The matcher generates lookalike token variants at engine init.

The full TR39 confusables corpus is intentionally not used at v0.1 — Cisco's pass-7 already covers the long tail; Pruner surfaces the discrete-signal layer.

## Test convention

Every rule needs a test at `wrapper/tests/rules/test_<RULE_ID>.py`:

```python
from pruner_wrapper.pack_runner import scan_rule_against_text

def test_positive_fixtures(rule_loader):
    rule = rule_loader("PI-FOO-001")
    for fixture in rule["fixtures"]["positive"]:
        assert scan_rule_against_text(rule, fixture)

def test_negative_fixtures(rule_loader):
    rule = rule_loader("PI-FOO-001")
    for fixture in rule["fixtures"]["negative"]:
        assert not scan_rule_against_text(rule, fixture)

def test_yaml_validates_against_schema(rule_loader, rule_v1_schema):
    rule = rule_loader("PI-FOO-001")
    rule_v1_schema.validate(rule)
```

Promotion to `status: stable` requires:

- All positive fixtures match.
- All negative fixtures don't match.
- FP measurement against `examples/benign-skill` and ≥ 3 public skill repos with rate ≤ 20 %.
- Schema-valid YAML.
