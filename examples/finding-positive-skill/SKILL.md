---
name: "Bad Name"
description: "Finding-positive fixture used by self-scan.yml to catch the 0.2.8 exit-code bug class. Trips four sub-critical Coroboros pack rules."
metadata:
  version: "1.0.0"
license: "Apache 2"
custom_field: "bar"
---

# Finding-positive

Trips Coroboros pack findings strictly below the `critical` threshold. The
`pruner-finding-positive` job in `.github/workflows/self-scan.yml` invokes the
composite via `uses: ./` against this fixture at `fail-on: critical` and
asserts the workflow goes green — `pruner scan` exit 1 (findings present, all
below threshold) must thread through `coroboros-pack-run` and the gate step
without being masked as a workflow failure. The 0.2.8 bug class.

See `EXPECTATIONS.md` for the rule cross-walk.
