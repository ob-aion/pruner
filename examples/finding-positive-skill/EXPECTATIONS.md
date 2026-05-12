# Finding-positive skill — expected findings

When `pruner scan examples/finding-positive-skill --without-cisco` runs, the
Coroboros pack should report exactly the following findings. Zero critical
by design.

| Rule | File | Severity | Why |
|---|---|---|---|
| FC001 | `SKILL.md` | high | `name` is `"Bad Name"` — contains a space, fails kebab-case. |
| FC003 | `SKILL.md` | medium | `custom_field` at top level (must live under `metadata:`). |
| FC004 | `SKILL.md` | low | `metadata.version` present (Coroboros house rule forbids it). |
| FC005 | `SKILL.md` | low | `license: "Apache 2"` is not a valid SPDX identifier (correct: `Apache-2.0`). |

The fixture exists to keep `pruner scan` exit 1 threaded through the composite
action under `fail-on: critical` — exit 0 is the expected outcome at the
workflow level. Distinct from `examples/vulnerable-skill/`, which trips 7
critical findings (PI-UNI-001/003 weight-locked at 1.00, PI-IDFILE-001 and
PI-EXFIL-002 on `scripts/`) and exists to validate the full Coroboros + Cisco
detection surface.
