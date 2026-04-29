# Architecture

## One-line model

`action.yml` (composite, SHA-pinned) → `wrapper/` Python package → Cisco subprocess + Coroboros pack + gitleaks + actionlint → `compose-report` → `report-v1.json` + SARIF + SBOM + SLSA provenance → `actions/attest-*` → release bundle + badge.

## Three briques

```
+------------------------------+   +------------------------------+   +------------------------------+
|  Brique 1: Detection         |   |  Brique 2: Coroboros pack    |   |  Brique 3: Attestation       |
|  ------------------          |   |  -----------------------     |   |  -----------------------     |
|  cisco-ai-skill-scanner      |   |  12 default-on rules:        |   |  SBOM via syft               |
|  (pinned, deterministic)     |+->|    FC001-FC005 (frontmatter) |+->|  attest-build-provenance     |
|  gitleaks (secrets)          |   |    PI-UNI-001..004 (Unicode) |   |  attest-sbom                 |
|  actionlint (workflows)      |   |    PI-PEP723-001 (deps)      |   |  Pruner Verified badge       |
|  snyk-agent-scan (opt-in)    |   |    PI-IDFILE-001 (identity)  |   |  release-asset bundle        |
|                              |   |    PI-MDIMG-001 (md-img)     |   |                              |
|                              |   |  12 opt-in PD rules          |   |                              |
+------------------------------+   +------------------------------+   +------------------------------+
            v                                  v                                  v
            +------------------ pruner compose --> report-v1.json -------------+
                                                                              |
                                                                              v
                                                            gh attestation verify (consumer)
```

## Composite action steps

`action.yml` is a composite GitHub Action — YAML only, every external `uses:` SHA-pinned. The 10-step sequence:

1. `setup-python` — pin a Python 3.12 (or consumer-overridable).
2. `setup-cisco` — install `cisco-ai-skill-scanner==2.0.9` into a fresh venv; verify Apache-2.0 marker; halt with lore-tagged message on drift.
3. `cisco-run` — invoke the Cisco scanner against the audited path; emit SARIF.
4. `coroboros-pack-run` — run `pruner scan --without-cisco --rules rules/`; emit SARIF.
5. `gitleaks-run` — secrets scan via `gitleaks/gitleaks-action`.
6. `actionlint-run` — workflow safety on the audited repo's `.github/workflows/`.
7. `snyk-run` (conditional) — only if `with-snyk: true` and `SNYK_TOKEN` is set; non-blocking second opinion.
8. `compose-report` — merge all SARIFs into `report-v1.json`; apply `.pruner-policy.yml` and `.pruner-ignore.yml`; compute per-category grade.
9. `emit-badge` — render `badge.svg` from grade + Coroboros design tokens.
10. `upload-sarif` + `gate` — push aggregated SARIF to GitHub Code Scanning; exit 0/1/2/3 per `fail-on`.

The composite is the **primary surface**. The reusable workflow at `.github/workflows/reusable-full-scan.yml` is a one-line consumer convenience that wraps the composite plus the attestation steps.

## Wrapper package structure

```
wrapper/
├── pyproject.toml              # pyyaml + cisco-ai-skill-scanner (pinned) + dev deps
├── CISCO_PIN.md                # pinned version, main-HEAD SHA, license marker
└── src/pruner_wrapper/
    ├── cli.py                  # argparse, exit codes, formatters
    ├── cisco_runner.py         # subprocess to skill-scanner
    ├── snyk_runner.py          # opt-in second opinion
    ├── pack_runner.py          # rule discovery + dispatch
    ├── source_confidence.py    # path-class weighting
    ├── compose.py              # SARIF merge + report-v1 emit
    ├── allowlist.py            # .pruner-ignore.yml
    ├── policy.py               # .pruner-policy.yml
    ├── badge.py                # SVG emitter
    ├── attestation.py          # report.attestation block populator
    ├── sarif.py                # SARIF 2.1.0 emit + parse
    ├── confusables.py          # 30-row Cyrillic/Greek table for PI-UNI-004
    ├── spdx.py                 # ~30 SPDX identifiers
    ├── lore.py                 # lore strings (ASCII, no emoji)
    ├── types.py                # Finding, Rule, ScanContext dataclasses
    └── matchers/
        ├── regex_matcher.py
        ├── absence_regex_matcher.py
        ├── codepoint_range_matcher.py
        ├── homoglyph_matcher.py
        ├── frontmatter_validator.py
        └── pep723_validator.py
```

## Schema contracts

`schema/rule-v1.json`, `schema/report-v1.json`, `schema/allowlist-v1.json`, `schema/policy-v1.json` — JSON Schema 2020-12. Stability: backward-compatible additions until next major; removals/renames require a major bump.

## Source confidence

Findings carry a `source_confidence` tag derived from the file path — continuous weight, not tier downgrade. See [`docs/writing-rules.md`](./writing-rules.md#source-confidence) for the path → tag mapping. Secrets and PI-UNI-* findings have `weight_override: 1.00` — invisible payloads are still invisible regardless of where they sit.

## Trust chain

1. **Engine** — `cisco-ai-skill-scanner` pinned at SHA, license-checked at install.
2. **Wrapper** — `pruner-wrapper` pinned to its own version inside the action.
3. **Wrapped actions** — every external `uses:` SHA-pinned; commented `# v1.2.3`.
4. **Build provenance** — `actions/attest-build-provenance` emits in-toto attestation.
5. **SBOM signing** — `actions/attest-sbom` over the syft-generated CycloneDX SBOM.
6. **Verification** — `gh attestation verify` against public-good Sigstore.

No Coroboros service is in the trust path.
