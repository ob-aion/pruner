# Coroboros policy pack

Twelve default-on rules + twelve opt-in PD rules. Every rule conforms to [`schema/rule-v1.json`](../schema/rule-v1.json).

## Default-on (12)

| Pillar | Rules |
|---|---|
| Frontmatter conformance | [`frontmatter-conformance/`](./frontmatter-conformance/) — FC001–FC005 |
| Unicode-Tag arsenal | [`unicode-tags/`](./unicode-tags/) — PI-UNI-001..004 |
| Supply-chain hygiene | [`supply-chain/`](./supply-chain/) — PI-PEP723-001, PI-IDFILE-001, PI-MDIMG-001 |

## Opt-in (12)

| Pillar | Rules |
|---|---|
| Prompt-defense posture | [`prompt-defense/`](./prompt-defense/) — PD001–PD012 |

The PD pack is **disabled by default**. Activate per repo via `.pruner-policy.yml`:

```yaml
version: 1
name: "Org Policy"
scan_prompt_defense_posture: true
```

## Anti-patterns explicitly NOT rules

To avoid FP flood:

- Mentioning "prompt injection" in security-aware docs.
- `TODO:` / `FIXME:` in comments.
- Long base64 strings without a decoded-shell heuristic.
- Comment-only shell lines (`# curl https://...`) — suppressed via `context_rules.skip_if_line_starts_with`.
- Defensive example text in security-review prompts (e.g. `fetch(userProvidedUrl)`) — suppressed via `context_rules.skip_if_path_matches`.
- **Rules covered by Cisco**, not duplicated here. Pruner's pack focuses on documented Cisco gaps.

Walkthrough: [`docs/writing-rules.md`](../docs/writing-rules.md).
