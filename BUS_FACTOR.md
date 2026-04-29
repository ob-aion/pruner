# Bus factor

Honest declaration of maintainer capacity, in keeping with Coroboros's "ship signal, not marketing" posture.

## Current state — 0.1.1

- **Bus factor: 1.** Single maintainer: `@ob-aion`.
- **Co-maintainer signal:** open at `help-wanted: co-maintainer` since v0.1.1.
- **Coverage if maintainer disappears:** the repo is Apache-2.0, every dependency is SHA-pinned, and the trust artefacts (signed report bundle, in-toto attestation) are independently verifiable via `gh attestation verify` against public-good Sigstore. Existing releases keep working. No new releases ship.

## Why this is tolerable at 0.x

Pruner keeps the engine surface in Cisco's hands. The Coroboros-owned code is a thin wrapper plus 24 YAML rules. A motivated contributor can fork, audit, and continue maintenance in a weekend.

## Mitigations

- **SHA-pinning everywhere.** Every wrapped action and the Cisco engine are pinned to specific versions documented in `wrapper/CISCO_PIN.md` and `.github/dependabot.yml`. A maintenance gap does not turn into a security regression overnight.
- **License-drift auto-halt.** The composite action refuses to run if the upstream Cisco LICENSE marker changes.
- **Monthly upstream probe.** `.github/workflows/cisco-upstream-check.yml` opens an `upstream-drift` issue automatically on archival, license change, or 90-day staleness.
- **Public attestation.** Verifiable signed bundle on every release means downstream consumers don't need a live maintainer to trust an existing artefact.
- **Documented swap path.** `docs/why-cisco.md` describes how to replace the Cisco engine if needed (fork at last-good SHA or substitute with `snyk/agent-scan`).

## What's NOT mitigated

- New rules in response to fresh threat-landscape changes require a human deciding what to add.
- FP-audit refinements on real consumer corpora require human classification.
- Breaking-change response to Cisco engine major versions requires human review.

## How to help

1. Open a `rule-proposal` issue with rationale + fixtures + FP measurement.
2. Open a `false-positive` issue when a rule fires on legitimate content; include a minimal reproducer.
3. Comment on the `help-wanted: co-maintainer` issue if you want commit access.

## Funding

Pruner is Apache-2.0, free, no telemetry, no commercial tier. GitHub Sponsors is configured discreetly under `coroboros`. OpenSSF donation conversations are post-1.0.
