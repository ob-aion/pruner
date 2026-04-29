# Verify a Pruner report

Anyone with a Pruner release asset can verify it independently — no Coroboros services in the trust path.

## What you're verifying

`pruner-report.zip` contains:

| File | Meaning |
|---|---|
| `report-v1.json` | The signed report — findings, allowlist, policy outcome, grade. |
| `sarif-bundle.tar.gz` | Aggregated SARIF (Cisco + Coroboros pack + gitleaks). |
| `sbom.cdx.json` | CycloneDX 1.5 SBOM of the audited surface. |
| `scorecard.json` | OpenSSF Scorecard JSON output. |
| `attestation.intoto.jsonl` | In-toto attestation (SLSA build provenance). |
| `badge.svg` | Pruner Verified badge for the release. |

## Tool

[GitHub CLI](https://cli.github.com/) `gh` ≥ 2.45 with `attestation` extension.

## Procedure

```bash
# 1. Download the report bundle from the release
gh release download <tag> --repo <owner>/<repo> --pattern 'pruner-report.zip'

# 2. Verify the build-provenance attestation
gh attestation verify pruner-report.zip --owner <owner>

# 3. (Optional) Verify the SBOM attestation
gh attestation verify pruner-report.zip --owner <owner> --predicate-type https://spdx.dev/Document
```

Successful verification looks like:

```
Loaded digest sha256:<hash> for file://pruner-report.zip
Loaded 1 attestation from GitHub API
[OK] Verification succeeded!

The following policy criteria were verified:
- predicate-type: https://slsa.dev/provenance/v1
- source-repository: https://github.com/<owner>/<repo>
- workflow trigger: push
```

## What success means

- The bundle was produced by a workflow run on the named GitHub repository.
- The workflow ran with `id-token: write` permission, signed via OIDC.
- The signature was issued by public-good Sigstore + GitHub's OIDC issuer.
- The bundle SHA matches the one recorded in the attestation.

## What success does NOT mean

- That the audited skill is safe to run on arbitrary inputs in arbitrary agents.
- That the report's findings classification is correct (read `report-v1.json`'s `policy_evaluation` and `findings[]`).
- That allowlisted findings are legitimate (`report-v1.json`'s `allowlisted[]` lists every suppressed finding with its justification — review them).

## Inspecting the report

```bash
unzip -p pruner-report.zip report-v1.json | jq '{summary: .summary, allowlisted_count: (.allowlisted | length), policy_compliant: .policy_evaluation.compliant}'
```

Reading the findings:

```bash
unzip -p pruner-report.zip report-v1.json | jq '.findings[] | {id, severity_effective, owasp_ast, location: .location.path, message}'
```

## If verification fails

`gh attestation verify` exits non-zero on:

- Missing attestation in the GitHub API.
- SHA mismatch between the file and the attestation subject.
- Wrong owner / wrong source repo.
- Sigstore certificate expired or not from the expected issuer.

This is the trust signal. **Do not trust an unverifiable report.** Treat it as if Pruner had not run.
