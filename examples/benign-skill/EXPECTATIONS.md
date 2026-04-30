# Benign skill — expected findings

When `pruner scan examples/benign-skill --without-cisco` runs against this fixture, the Coroboros pack should produce **zero** findings.

```bash
pruner scan examples/benign-skill --without-cisco --format json --output /tmp/benign.json
jq '.findings | length' /tmp/benign.json   # → 0
```

If any finding fires, the regression is real — open a `false-positive` issue with the rule ID and the offending line.
