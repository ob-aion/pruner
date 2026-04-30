# SHA pinning — tag-object vs commit

Every third-party `uses:` line in this repo is SHA-pinned with a `# vX.Y.Z` comment. Two kinds of git object can sit behind a 40-char hex SHA:

1. **A commit object.** What you want.
2. **An annotated-tag object.** What you do not want.

Both are valid SHAs and both `git checkout` cleanly. GitHub Actions accepts either at runtime — the workflow runs. The OpenSSF Scorecard webapp does not. When it uploads results, it checks the pinned SHA resolves to a real commit in the upstream repository. Tag-object SHAs are rejected with a 400 / `imposter commit` error. The SARIF still lands in Code Scanning but the published score on `securityscorecards.dev` never updates.

This is how `0.1.0` through `0.1.3` shipped with `ossf/scorecard-action@99c09fe975337306107572b4fdf4db224cf8e2f2` and `github/codeql-action/upload-sarif@865f5f5c36632f18690a3d569fa0a764f2da0c3e` — both pinned to tag objects rather than commits. `0.2.0` corrected both.

## Resolve a tag to its commit

When pinning a new action or bumping an existing one, never copy the SHA reported by `git ls-remote` against an annotated-tag ref — that SHA is the tag object. Instead:

```bash
TAG=v2.4.3
gh api repos/<owner>/<repo>/git/refs/tags/$TAG --jq '.object.type, .object.sha'
```

If `.object.type` is `commit`, the SHA is the commit — pin it directly. If it is `tag`, drill the annotated-tag indirection:

```bash
TAG_OBJ=$(gh api repos/<owner>/<repo>/git/refs/tags/$TAG --jq '.object.sha')
gh api repos/<owner>/<repo>/git/tags/$TAG_OBJ --jq '.object.sha'
```

The second SHA is the commit. That is what goes into the `uses:` line, with the original tag preserved as the `# vX.Y.Z` comment for human readability.

## Pre-flight verification

`scripts/verify-action-pins.sh` walks every `.github/workflows/*.yml` and `action.yml`, extracts each SHA-pinned `uses:` line, and calls the upstream `commits` API for each. Any 422 / 404 response means the SHA is not a commit (typically a tag object). The script exits non-zero on any failure.

It is wired into `release.yml` as a pre-flight step so a bad pin halts the release before the tag is cut. Run it manually before opening a Dependabot review or a manual SHA bump:

```bash
bash scripts/verify-action-pins.sh
```

Dependabot itself resolves to commit SHAs correctly when it opens a bump PR, so the bug class is mostly introduced by manual pins. The pre-flight catches both paths.
