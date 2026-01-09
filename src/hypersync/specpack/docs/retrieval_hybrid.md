
# Hybrid ANN → Exact-within-r Retrieval

This pack adds a metric-correct hybrid retrieval mode:
1) ANN prunes the space (e.g., HNSW-hyperbolic).
2) Exact refinement evaluates all candidates within radius r using the true metric.
3) An Exactness Receipt attests the parameters and reproducibility.

Files:
- Schemas: `schemas/retrieval/hybrid.config.v1.json`, `schemas/retrieval/exactness.receipt.v1.json`
- Examples: `artifacts/retrieval/examples/hyperbolic_hybrid.config.json`, `artifacts/retrieval/examples/retrieval_exactness.receipt.example.json`
- Policy: `policies/retrieval/hybrid_policy.json`
- CLI: `tools/retrieval/retrieval_cli.py`

Quick start:
```bash
# List example configs
python tools/retrieval/retrieval_cli.py list

# Emit a structure-only exactness receipt from a config
python tools/retrieval/retrieval_cli.py emit --config artifacts/retrieval/examples/hyperbolic_hybrid.config.json --query_commitment sha256:Q --index_commitment sha256:IDX --codebook_commitment sha256:CB --candidate_count 312 --radius 0.315

# Validate a receipt structure
python tools/retrieval/retrieval_cli.py validate --receipt artifacts/retrieval/receipts/exactness_*.receipt.json
```

Determinism & Attestation:
- Record `seed`, `tie_break`, ANN `ef_runtime`, and chosen `r`.
- Receipts are non-invertible attestations (commitments only).
