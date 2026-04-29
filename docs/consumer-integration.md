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

## Verifying a published report

Anyone with the release asset can verify the bundle:

```bash
gh release download <tag> --repo <owner>/<repo> --pattern 'pruner-report.zip'
gh attestation verify pruner-report.zip --owner <owner>
```

Walkthrough: [`docs/verify-a-report.md`](./verify-a-report.md).
