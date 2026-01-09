# ICO Sync 1.0 (Draft)

Purpose
- Replication and orchestration profile for ICO. Provides curvature-safe CRDT/OT semantics, deterministic replay, and audit.

Core Objects
- SyncDescriptor: { profile, dimension, invariants, merge_policy, numeric_policy }
- OpRecord: { id, causal: {vc|lc}, op: {kind, args}, pre, post }
- Snapshot: { state, policy_hash, proofs }
- AuditCapsule: { snapshot_id, log_range, invariants_verified }

Merge Policies (examples)
- E: vector-space CRDT with deterministic tie-breakers.
- S: compose geodesic moves + projection; guard antipodal cut locus.
- H: reject spacelike ops; exact PT and exp/log within envelope.

Determinism
- deterministic=true enforces fixed ordering on causal ties and seeded RNG.

