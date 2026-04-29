# Consumer integration

How a downstream agent skill repository adopts Pruner.

## Step 1 — Workflow

Drop this into `.github/workflows/pruner.yml`:

```yaml
name: Pruner — Security Audit
on:
  pull_request:
  push:
    tags: ['[0-9]+.[0-9]+.[0-9]+']
  schedule:
    - cron: '0 6 * * 1'   # weekly Monday 06:00 UTC catches drift between releases
  workflow_dispatch:

permissions:
  contents: read
  security-events: write
  id-token: write
  attestations: write

jobs:
  audit:
    uses: coroboros/pruner/.github/workflows/reusable-full-scan.yml@0.1.0
    with:
      fail-on: medium
      skill-pattern: 'skills/*/SKILL.md'
      report-output: ./.pruner
      scan-prompt-defense-posture: false
    secrets: inherit   # SNYK_TOKEN if you want the opt-in second opinion
```

## Step 2 — Badges

Add to your README:

```markdown
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/<owner>/<repo>/badge)](https://deps.dev/github/<owner>%2F<repo>)
[![Pruner Verified](https://github.com/<owner>/<repo>/releases/latest/download/pruner-badge.svg)](https://github.com/<owner>/<repo>/releases/latest)
```

At v0.1 the Pruner badge is committed-per-release SVG served from the latest release-asset URL. Later versions move to a hosted endpoint at `reports.coroboros.com`.

## Step 3 — SECURITY.md

Copy the scaffold from [`templates/SECURITY.md.tmpl`](../templates/SECURITY.md.tmpl) to your repo root and fill in:

- Maintainer handle
- SLA preferences (default 72h / 7d / 30d / 90d)
- Disclosure email or GitHub Security Advisory URL

## Step 4 — Allowlist (only if needed)

Pruner's discipline is "fail closed, allowlist with justification." Start with no allowlist. If a finding is a documented false positive, add to `.pruner-ignore.yml`:

```yaml
version: 1
ignores:
  - rule: PI-MDIMG-001
    path: docs/threat-examples.md
    justification: "Document illustrates exfil syntax for educational purposes; URLs are illustrative."
    expires: 2027-01-01
```

Schema: [`schema/allowlist-v1.json`](../schema/allowlist-v1.json). A missing `justification` halts the action with exit 3.

## Step 5 — Policy (optional)

For org-level governance, commit `.pruner-policy.yml`:

```yaml
version: 1
name: "Org Skills Policy"
min_score: 85
max_severity: high
banned_rules_bypass: ["PI-IDFILE-001", "PI-UNI-001"]
required_scans: [cisco, coroboros-pack]
required_attestation: true
scan_prompt_defense_posture: false
forbidden_paths:
  - "**/.env*"
  - ".claude-plugin/marketplace.json.bak"
```

Schema: [`schema/policy-v1.json`](../schema/policy-v1.json). Failing policy fails the workflow regardless of `fail-on`.

## Step 6 — Update CLAUDE.md / CONTRIBUTING.md

Add to your skill-author checklist:

> **Pruner runs on every PR and tag.** A failing Pruner blocks merge. Allowlist entries require a written justification in `.pruner-ignore.yml`.

## Snyk second opinion

Optional. `coroboros/pruner` accepts `snyk/agent-scan` as a second-opinion runner; off by default.

Snyk uplinks scan content to its cloud — incompatible with Pruner's air-gap default. Use only for content not subject to private or regulated handling. Background on the trade-off: [`docs/why-cisco.md#considered-alternatives`](./why-cisco.md#considered-alternatives).

### Setup

1. **Generate a `SNYK_TOKEN`.** From <https://app.snyk.io/account>, copy the API token.
2. **Add it as a repo secret.** Settings → Secrets and variables → Actions → New repository secret → name `SNYK_TOKEN`.
3. **Pass the secret through and flip `with-snyk`.**

```yaml
jobs:
  audit:
    uses: coroboros/pruner/.github/workflows/reusable-full-scan.yml@0.1.0
    with:
      fail-on: medium
      with-snyk: true
    secrets:
      SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

Without a token, the snyk step is silently skipped — the workflow does not fail.

### Snyk binary

The composite action invokes `snyk` via `command -v snyk`. `ubuntu-latest` runners do not pre-install Snyk; without an explicit install step the runner silently skips Snyk findings even when the token is present. The reusable workflow does not expose pre-step injection at 0.1.0, so wiring Snyk in requires the composite action directly:

```yaml
jobs:
  audit:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
      id-token: write
      attestations: write
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd  # v6.0.2
      - run: npm install -g snyk
      - uses: coroboros/pruner@0.1.0
        with:
          fail-on: medium
          with-snyk: true
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

Snyk findings land in the report's `tools[]` block with `mode: second-opinion, blocking: false`.

## Verifying a published report

Anyone with the release asset can verify the bundle:

```bash
gh release download <tag> --repo <owner>/<repo> --pattern 'pruner-report.zip'
gh attestation verify pruner-report.zip --owner <owner>
```

Walkthrough: [`docs/verify-a-report.md`](./verify-a-report.md).
