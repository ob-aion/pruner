---
name: "Bad Name"
description: "Finding-positive fixture used by self-scan.yml to catch the 0.2.8 exit-code bug class. Trips four sub-critical Coroboros pack rules."
metadata:
  version: "1.0.0"
license: "Apache 2"
custom_field: "bar"
---

# Finding-positive

Trips Coroboros pack findings strictly below the `critical` threshold.

The `pruner-finding-positive` job in `.github/workflows/self-scan.yml` invokes the composite via `uses: ./` against this fixture at `fail-on: critical`. Green outcome asserts the workflow stays green. `pruner scan` exit 1 (findings present, below threshold) must thread through `coroboros-pack-run` and the gate step. The 0.2.8 bug class.

See `EXPECTATIONS.md` for the rule cross-walk.
