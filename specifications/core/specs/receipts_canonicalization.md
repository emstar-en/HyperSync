# Receipts Canonicalization and Deterministic Replay

Canonical form:
- Field order: lexicographic by key.
- Float quantization: round-to-even at 1 ULP for fp16/bf16 fields; promote to fp32 before hashing.
- Timestamps: logical monotone clock per shard (no wall time) excluded from hash.
- Hash: SHA-256 over canonical JSON (UTF-8, LF newlines).

Replay contract:
- Given (inputs, numeric_policy_version, state_version) → outputs are bitwise identical.
- Dedupe key = H(tenant, id, state_version, op_kind).
