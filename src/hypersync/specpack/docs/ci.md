# CI Integration

Run all conformance vectors in CI and produce JUnit XML:

```bash
hs confrun --suite conformance/suites/all_profiles_all_vectors.suite.json --format junit --out reports/conformance.xml
```

Coverage report is written to conformance/coverage.json.
