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

The fixture keeps `pruner scan` exit 1 threaded through the composite action under `fail-on: critical`. Workflow exit 0 is the expected outcome.

## Dual-path allowlist behaviour

The repo-root `.pruner-ignore.yml` lists each of the four findings keyed by the path `examples/finding-positive-skill/SKILL.md`. Two scan contexts read that file:

| Job | `target-path` | Finding path | Allowlist match | Findings |
|---|---|---|---|---|
| `pruner-self-scan` | `.` | `examples/finding-positive-skill/SKILL.md` | yes | suppressed (Security tab + PR review stay clean) |
| `pruner-finding-positive` | `examples/finding-positive-skill` | `SKILL.md` | no | fire (exit-code propagation gets exercised) |

The path-based asymmetry is intentional and mirrors the existing 14 `examples/vulnerable-skill/` entries.

## Distinct from vulnerable-skill

`examples/vulnerable-skill/` trips 7 critical findings (PI-UNI-001 / PI-UNI-003 weight-locked at 1.00; PI-IDFILE-001 and PI-EXFIL-002 on `scripts/`) and validates the full Coroboros + Cisco detection surface. This fixture trips four sub-critical findings and validates a single composite-action contract.
