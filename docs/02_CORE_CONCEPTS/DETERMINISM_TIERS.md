# Hierarchical Determinism

This section defines how HyperSync maintains strong determinism guarantees
in a deeply nested, recursively orchestrated system.

## 0. Determinism tiers (recap)

HyperSync uses a small set of named determinism tiers (see determinism_tiers.json):

- D(0) Bit-Exact  
  Same inputs, same receipts, same numeric outputs bit-for-bit. All sources
  of randomness are derived from recorded configuration and merkleized seeds.

- D(1) Replayable  
  Same inputs and recorded randomness produce the same observable behavior.
  Local non-critical jitter is allowed, but a replay engine can reconstruct
  an equivalent execution trace from the seed and receipts.

- D(2) Statistical  
  The system is stochastic but bounded: ensembles of runs converge to
  well-defined distributions and diagnostics, even if individual runs differ.

- D(3) Best-Effort  
  No formal guarantees beyond basic safety. Used only for exploratory or
  non-critical flows.

In this document, "determinism" refers to the guarantees associated with a
Holon and its sub-graph as configured by determinism_config in the Holon
Definition schema.

---

## 1. The challenge

How do we maintain D(0) or D(1) determinism when thousands of users are
spawning nested sub-universes (Holons) in parallel, possibly on heterogeneous
hardware and over long time horizons?

Constraints:

- Holons may be created and destroyed dynamically.
- Holons may run at different logical tick rates (time dilation).
- Holons may partially overlap in their resource usage and topology.
- We still want local replay and diagnosis without replaying the entire
  universe from the Big Bang.

---

## 2. The Merkle Seed Tree

Determinism in HyperSync flows down the tree like a river. Every Holon and
Agent is assigned a seed derived from its parent context via a simple,
rigorously defined grammar.

### 2.1 Seed derivation

1. Root seed: the universe starts with a master seed S0 recorded in the
   root Holon's determinism_config.root_seed.
2. Holon seed: when Holon A is spawned, its seed SA is derived
   deterministically:

   SA = H(S0 || "holon" || HolonID || Tick_create || Salt_A)

3. Agent seed: when Agent X is spawned inside Holon A, its seed SX
   is derived from SA:

   SX = H(SA || "agent" || AgentID || Tick_spawn || Salt_X)

Where:

- H is a fixed, D(0)-qualified hash function family.
- HolonID and AgentID are stable identifiers recorded in receipts.
- Tick_create and Tick_spawn are logical tick numbers at which the
  entity was created.
- Salt_A and Salt_X are optional, recorded salts that allow partitioning
  of randomness across roles (for example planning vs sampling) without
  breaking replayability.

Rule: seeds are never sampled from ambient randomness. They are always
derived from recorded values and a deterministic hash.

### 2.2 Seed namespaces

To avoid collisions and to enable fine-grained control, the seed grammar
supports explicit namespaces:

- "holon"   - hierarchical orchestration and environment state.
- "agent"   - individual cognitive or behavioral processes.
- "channel" - communication channels such as message queues.
- "run"     - user-initiated runs or experiments.

Each namespace can define its own sub-structure for instance_id and
context_salt, but all must remain derivable from receipts.

---

## 3. Local causality and replay

Because SA depends only on S0 and A's creation parameters, Holon A is
replayable in isolation.

You do not need to replay the entire universe to debug the Marketing
Department. You only need:

- the Holon's determinism_config (including root_seed),
- the Holon's topology and configuration at creation time,
- the Holon's inbound receipts (external inputs across its boundaries).

We call this bundle a replay recipe.

Example (informal):

{
  "holon_id": "holon_research_001",
  "determinism_tier": "D0_BIT_EXACT",
  "root_seed": "seed:...",
  "config_hash": "sha256:...",
  "inbound_receipts": ["receipt:...", "receipt:..."]
}

For D(0) and D(1) Holons, the replay recipe is sufficient to re-materialize
an equivalent execution trace on a clean fabric.

---

## 4. Clock domains and time dilation

Time in HyperSync is logical (ticks).

- Global clock (root Holon): ticks at a steady base rate as defined by the
  root Holon's determinism_config.tick_rate.
- Local clocks (child Holons): each Holon can run at its own time dilation
  factor relative to its parent.

Example configurations:

- A simulation Holon runs 1000 ticks for every 1 root tick.
- A UX Holon ticks only on user interaction.

The mapping between parent and child clocks is recorded as part of the
Holon's determinism_config.clock_sync_strategy, for example:

{
  "clock_sync_strategy": "locked_ratio",
  "parent_ticks_per_child_tick": 0.001
}

Invariant: all cross-Holon interactions must cross an Acceptance Gate that
snaps events to well-defined tick boundaries on both sides. This keeps local
time dilation from corrupting global determinism.

---

## 5. Cross-Holon interactions

Holons can communicate along two primary classes of channels:

1. Deterministic channels (D0 and D1):
   - Messages are ordered, deduplicated, and checkpointed.
   - The sending Holon's tick and the receiving Holon's tick are recorded in
     each message receipt.
   - Replays must respect these causal edges.

2. Statistical channels (D2 and D3):
   - Messages may be sampled, dropped, or reordered within bounded policies.
   - Determinism is defined in terms of distributions and diagnostics, not
     individual messages.

For each Holon, the determinism_config specifies which channels are permitted
and how they are reconciled at the boundary.

---

## 6. Operational patterns

### 6.1 Debugging a single Holon

1. Fetch the Holon's replay recipe from receipts or from the API.
2. Provision an isolated test fabric.
3. Re-run the Holon using the recorded seeds and inbound receipts.
4. Compare outputs against production receipts for divergence.

### 6.2 Safely mixing determinism tiers

A common pattern is to combine:

- A D(0) or D(1) control Holon (orchestrating and enforcing safety).
- Multiple D(2) exploratory Holons (large Monte Carlo sweeps, search, etc.).

The control Holon consumes summarized receipts from exploratory Holons
through Acceptance Gates that enforce snapping, aggregation, and
thermodynamic gating. This allows large-scale exploration without
poisoning the deterministic control layer.

---

## 7. Summary

The Merkle Seed Tree plus disciplined clock domains give HyperSync:

- Local, composable replay of complex Holons.
- Clear separation between deterministic control and exploratory dynamics.
- A compact, mechanical replay recipe that any compatible fabric can
  execute.

This structure allows effectively unbounded D(2) scaling because the
statistical variance of one department does not pollute another unless
you explicitly wire them together.
