
# Non-Volatile Memory (NVM) Blocks

This pack defines policy-gated NVM blocks as durable, non-invertible artifacts usable by an array of models within the same LD and profile.

- Schemas: `schemas/nvm/*`
- Examples: `artifacts/nvm/examples/*`
- Receipts: `artifacts/nvm/receipts/*`
- CLI: `tools/nvm/nvm_cli.py`

Quickstart:

```bash
# List example blocks
python tools/nvm/nvm_cli.py list

# Validate a descriptor
python tools/nvm/nvm_cli.py validate --block artifacts/nvm/examples/hyperbolic_kg.v3.json

# Commit a block (emits BlockWriteReceipt)
python tools/nvm/nvm_cli.py commit --block artifacts/nvm/examples/hyperbolic_kg.v3.json --writer entity://E42/modelrouter --profile ADVANCED --inputs sha256:input1 sha256:input2
```

Security posture:
- No raw inputs or raw vectors are stored.
- Embeddings should be quantized (OPQ/PQ codes) and geometry-aware.
- All writes produce receipts with payload commitments and policy hits.

## Hardware Profiles and Bootstrap Expectations

Generated runtimes that use this NVM schema are expected to:

- Create or locate a `hardware_profile` document conforming to
  `03_specifications/environment/hardware_profile.schema.json` during
  first-run.
- Use NVM to persist this profile and to initialize at least:
  - A system docs/specs block.
  - A default user workspace block.
  - A system experience block.
- Participate in the first-run sequence described in
  `07_documentation/first_run_nvm_bootstrap.md`.
