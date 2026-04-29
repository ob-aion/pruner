# Examples — cross-walk

Two reference fixtures used by the wrapper integration tests and consumer onboarding.

| Fixture | Expected findings | Cross-walk |
|---|---|---|
| [`vulnerable-skill/`](./vulnerable-skill/) | At least 9 findings across FC, PI-UNI-001, PI-UNI-003, PI-MDIMG, PI-IDFILE, PI-PEP723. | [`vulnerable-skill/EXPECTATIONS.md`](./vulnerable-skill/EXPECTATIONS.md) |
| [`benign-skill/`](./benign-skill/) | Zero findings. | [`benign-skill/EXPECTATIONS.md`](./benign-skill/EXPECTATIONS.md) |

Smoke-test the wrapper:

```bash
pruner scan examples/vulnerable-skill --without-cisco
pruner scan examples/benign-skill     --without-cisco
```

PI-UNI-002 (variation selectors) and PI-UNI-004 (homoglyphs) are not triggered by the integration fixtures; their unit-test fixtures live under `wrapper/tests/`.
