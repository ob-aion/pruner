# Security policy

## Reporting a vulnerability

Open a private vulnerability report at <https://github.com/ob-aion/pruner/security/advisories/new>. Do not file a public issue. Do not email.

**SLA**

- Acknowledge: 72 hours
- Triage: 7 days
- Fix critical: 30 days
- Fix high: 90 days

CVE requested via GitHub Security Advisories when warranted.

## Scope

Pruner is a CI-only audit tool that runs on the publishing side of an agent skill repository. It does not execute scanned skills, does not load them into a runtime, does not phone home, and does not require network access for the deterministic phases.

Full threat model — what's in scope, what's out, and what nothing covers: [`docs/threat-model.md`](./docs/threat-model.md). Coverage matrix per rule: [`docs/coverage-matrix.md`](./docs/coverage-matrix.md). Audit-the-auditor (Pruner's own attack surface and self-defenses): [`docs/threat-model.md#audit-the-auditor`](./docs/threat-model.md#audit-the-auditor).

## Trust model

The composite action runs entirely on GitHub-hosted or self-hosted runners belonging to the consumer. Pruner produces a signed report bundle that consumers verify with `gh attestation verify` against the public-good Sigstore instance and GitHub OIDC. No Coroboros service is in the trust path.

## Disclosure history

None published.
