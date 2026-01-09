# HyperSync Core Consensus Capsules d Logic Specification (Enhanced)

## 1. Purpose and Scope

The **HyperSync Core Consensus** capsule family (`hypersync.core.consensus.*`) provides deterministic, geometry-aware consensus for:

- Environment state (which capsules, policies, and configurations are active).  
- Environment upgrades (capsule version changes, schema migrations).  
- Critical safety gates (enabling/disabling capabilities, changing fences).  
- Multi-node and multi-tenant coordination.

Consensus capsules must support **bit-exact determinism (D0_bit_exact)** for core decision logic and produce auditable receipts for every decision.

---

## 2. Conceptual Model

### 2.1 Environment Views and Proposals

Consensus operates over **Environment Views**:

- An Environment View is a snapshot of:
  - Active capsules (IDs, versions, determinism tiers).  
  - Active schemas and policies.  
  - Active geometry spaces and fences.  
  - Active tenant and session environments.

Changes to the environment are represented as **Proposals**:

- Upgrade or downgrade a capsule version.  
- Activate or deactivate a policy.  
- Modify or add a geometric space or fence.  
- Change resource allocations or trust zones.

### 2.2 Quorums and Roles

Consensus protocols maintain safety and liveness across participants:

- **Proposers** suggest environment changes.  
- **Voters** evaluate proposals against policy and determinism constraints.  
- **Learners / Observers** subscribe to decisions and update local state.

Roles may be bound to tenants, nodes, or dedicated control planes.

---

## 3. Core Operations and APIs

Consensus capsules expose deterministic operations over proposals and views.

### 3.1 Proposal Lifecycle

- `Propose(environment_id, proposal, options)`  
  Submit a new proposal to change an environment. Returns a proposal handle.

- `Vote(environment_id, proposal_id, vote, metadata)`  
  Cast a vote on a proposal (accept, reject, abstain) with rationale.

- `Decide(environment_id, proposal_id)`  
  Finalize the outcome of a proposal (accepted, rejected, superseded) and emit a decision.

### 3.2 View Management

- `GetView(environment_id)`  
  Returns the current committed view of the environment.

- `ListDecisions(environment_id, filter)`  
  Enumerates historical decisions and associated receipts.

- `Subscribe(environment_id, cursor)`  
  Streams decisions for an environment, enabling nodes and agents to track changes.

### 3.3 Safety and Policy Checks

Before admitting a proposal into the consensus pipeline, the capsule must:

- Validate that the proposal is **well-formed** according to schemas.  
- Check that requested changes are **permitted by policy** (e.g., allowed namespace, determinism tiers).  
- Ensure that proposed changes remain within **geometry fences** (for spatial configurations).

Proposals that fail these pre-checks are rejected deterministically with structured error reasons.

---

## 4. Geometry-Aware Consensus

Consensus integrates with geometry capsules to reason about **topology and placement**:

- Environment views may include geometric descriptors of node locations, data shards, and fences.  
- Proposals may request changes to geometry (e.g., adding a new region of interest).

Consensus must:

- Ensure that geometry changes preserve **safety invariants** (e.g., no overlapping forbidden regions).  
- Handle changes in topology gracefully (e.g., nodes entering/leaving regions).  
- Maintain deterministic behavior regardless of physical topology, within the declared determinism tier.

---

## 5. Determinism and Receipts

### 5.1 Determinism Tier

Core consensus capsules declare `determinism_tier = D0_bit_exact` for decision logic:

- Given the same sequence of proposals and votes, all correct participants must compute the **same sequence of decisions**.  
- Randomized leader election (if used) must be derived from deterministic inputs (e.g., receipts, previous decisions) or isolated in non-core capsules.

### 5.2 Consensus Receipts

Every consensus decision emits a **consensus receipt** that records:

- Environment ID and view version (before and after).  
- Proposal ID, payload hash, and schema references.  
- Quorum details (voters, weights, decisions).  
- Capsule ID and version, determinism tier, and manifest hash.  
- Any referenced geometry receipts (for geometry-aware changes).

These receipts are essential for:

- Reconstructing environment evolution over time.  
- Auditing who/what proposed changes and why they were accepted.  
- Debugging misconfigurations or unexpected behaviors.

---

## 6. Security, Governance, and AI Containment

Consensus capsules enforce **governance** over environment changes:

- Only authorized roles may propose changes to core capsules or policies.  
- Untrusted AI agents cannot directly mutate environment views; they must go through mediated workflows.

Policies (see `capsules_hypersync.core.consensus_spec_policy.ENHANCED.yaml`) dictate:

- Which namespaces are allowed in proposals (e.g., `tenant.*` but not `hypersync.core.*`).  
- Which determinism tiers are acceptable in critical paths.  
- Which changes require multi-party human approval vs. automated policies.

This ensures that the **environment in which AI operates** is:

- Stable and well-governed.  
- Traceable from initial bootstrap through every change.  
- Resistant to unilateral or accidental destabilization by agents.
