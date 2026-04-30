# Repository secrets

Pruner runs offline by default. The deterministic pipeline — Cisco subprocess, Coroboros pack, `gitleaks`, `actionlint`, attestation — needs no tokens. Two optional secrets opt into specific features.

## `SCORECARD_TOKEN` (maintainer-side)

Used by [`.github/workflows/scorecard.yml`](../.github/workflows/scorecard.yml). The default `GITHUB_TOKEN` cannot read classic branch-protection rules, so OpenSSF Scorecard's Branch-Protection check returns `-1` (inconclusive) without a fine-grained PAT.

The workflow resolves `repo_token: ${{ secrets.SCORECARD_TOKEN || secrets.GITHUB_TOKEN }}`. Without the secret it falls back to `GITHUB_TOKEN` and behaves as before. Branch-Protection stays inconclusive in that case.

### Setup

1. GitHub → Settings → Developer settings → Personal access tokens → Fine-grained → **Generate new token**.
2. **Resource owner**: the org or user that owns the repo (e.g., `ob-aion`). **Repository access**: only the Pruner repo. **Expiration**: maximum the policy allows; rotate before expiry.
3. **Repository permissions**: `Administration: Read-only`. The Scorecard action also reads basic repo metadata, which is implicit.
4. **Generate token**, copy the value.
5. Repo → Settings → Secrets and variables → Actions → **New repository secret** → name `SCORECARD_TOKEN`, paste the value.
6. Trigger the next Scorecard run via `gh workflow run scorecard.yml` and confirm Branch-Protection reports a real score at `https://api.securityscorecards.dev/projects/github.com/<owner>/<repo>`.

### Scope discipline

`SCORECARD_TOKEN` is read-only. It cannot push, merge, or modify settings. Even so, mint the narrowest fine-grained PAT possible (single repository, single permission, near-term expiry).

## `SNYK_TOKEN` (consumer-side, opt-in)

Used by the composite action's optional `snyk-agent-scan` second-opinion runner. Setup walkthrough, cloud-uplink trade-off, and behaviour when the secret is unset: [`docs/consumer-integration.md#snyk-second-opinion`](./consumer-integration.md#snyk-second-opinion).

## What no token covers

The default deterministic pipeline runs without any token:

- Cisco engine (`cisco-ai-skill-scanner`, Apache-2.0, fully local).
- Coroboros pack (28 rules, YAML, fully local).
- `gitleaks` (CLI, MIT, fully local, no API calls).
- `actionlint` (binary, fully local).
- Attestation via [`actions/attest-build-provenance`](https://github.com/actions/attest-build-provenance) + [`actions/attest-sbom`](https://github.com/actions/attest-sbom) — uses GitHub's built-in `id-token` permission and the public-good Sigstore instance.

Pruner emits a signed bundle that downstream consumers verify with `gh attestation verify` against public-good Sigstore + GitHub OIDC. **No token is required for verification.** No Coroboros service is in the trust path.
