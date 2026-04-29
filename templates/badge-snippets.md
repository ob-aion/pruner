# Badge snippets

Drop into your README to advertise Pruner verification on your skill repo.

## Pruner Verified — release-asset SVG

```markdown
[![Pruner Verified](https://github.com/<OWNER>/<REPO>/releases/latest/download/pruner-badge.svg)](https://github.com/<OWNER>/<REPO>/releases/latest)
```

The badge is committed to each release as `pruner-badge.svg` by the composite action. Until `reports.coroboros.com` ships (post-1.0), the badge is served directly from the latest release-asset URL.

## OpenSSF Scorecard

```markdown
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/<OWNER>/<REPO>/badge)](https://deps.dev/github/<OWNER>%2F<REPO>)
```

## Three-badge row (recommended)

```markdown
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/<OWNER>/<REPO>/badge)](https://deps.dev/github/<OWNER>%2F<REPO>)
[![Pruner Verified](https://github.com/<OWNER>/<REPO>/releases/latest/download/pruner-badge.svg)](https://github.com/<OWNER>/<REPO>/releases/latest)
[![CodeQL](https://github.com/<OWNER>/<REPO>/actions/workflows/codeql.yml/badge.svg)](https://github.com/<OWNER>/<REPO>/actions/workflows/codeql.yml)
```

Three badges max — more is noise. Never add Snyk, SonarCloud, or commercial-tier badges.

## Verification snippet

Pair the badge with a verification snippet so consumers can audit independently:

````markdown
## Verifying the security report

```bash
gh release download <tag> --repo <OWNER>/<REPO> --pattern 'pruner-report.zip'
gh attestation verify pruner-report.zip --owner <OWNER>
```

Walkthrough: <https://github.com/coroboros/pruner/blob/main/docs/verify-a-report.md>.
````
