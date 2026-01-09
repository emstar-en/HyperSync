# Persistent Memory (Optional)

Provides an opt-in, compliant persistent memory layer for HyperSync while preserving geometry-native, storeless defaults.

Modes:
- pointer_only: store content-address pointers and typed predicates; no payloads.
- payload_redacted: store redacted snippets with PII/secrets masked/hashed.
- payload_encrypted: store minimal payloads encrypted at rest (KMS/HSM keys), WORM-capable.

Guarantees:
- vectors_at_rest=false by default; raw embeddings/distances are not persisted.
- strong TTL + crypto-erasure; legal_hold_override handled via Audit Capsule.
- typed receipts only; allowlist logging; DP aggregates.

Backend layout examples for Cassandra/Scylla/Postgres are provided in templates.
