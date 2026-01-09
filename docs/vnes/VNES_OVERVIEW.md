# Vector-Native Extension System (VNES) – Overview (Enhanced)

## 1. Role in HyperSync

The **Vector-Native Extension System (VNES)** is the universal runtime and development plane for HyperSync. Instead of a narrow "core vs. plugin" model, HyperSync treats almost all behavior as **Vector Capsules** that can be:

- Discovered via vector search over documentation and capabilities.
- Loaded and verified deterministically via manifests and receipts.
- Composed into higher-order workflows by both humans and AI agents.

In practice, this means that HyperSync's geometry kernels, consensus engines, TUI layouts, audio themes, diagnostic overlays, and user-defined strategies are **all instances of the same abstraction**. VNES provides the common language for describing, verifying, and orchestrating those behaviors.

---

## 2. Core Principles

### 2.1 Everything Is a Capsule (But Typed)

"Everything is a capsule" does **not** mean everything is a blob. Capsules are strongly typed and classified:

- **Logic capsules** – algorithms, kernels, solvers, policies.
- **Pipeline capsules** – orchestrations of multiple capsules into a reusable flow.
- **UI capsules** – TUI layouts, projection recipes, style themes, raster strategies.
- **Dataset capsules** – structured data bundles with schemas and provenance.
- **Driver / adapter capsules** – external connectors (I/O, storage, messaging).
- **Policy capsules** – constraints, limits, and governance rules.
- **Test & validation capsules** – golden vectors, conformance suites.

The capsule **type** and its **capabilities** are declared in the manifest and enforced by the runtime.

### 2.2 Vector-Native Discovery

All capsules are indexed by **high-dimensional embeddings** derived from:

- Natural-language documentation (specs, comments, usage guides).
- Formal capability declarations (input/output schemas, determinism tier).
- Observed behavior (telemetry and receipts, when appropriate).

AI agents and tools do not hard-code capsule IDs. Instead they issue **semantic queries** such as:

- "hyperbolic geometry distance function suitable for D(0)".
- "heatmap renderer for high-frequency tensors on terminal".

The VNES Registry resolves these to concrete, versioned capsule IDs and exposes explanations of why they matched.

### 2.3 Spec-First, Receipt-Backed

VNES is **spec-driven**:

1. A capsule begins life as a **Specification Capsule** (manifest + spec/ tree).
2. The STUNIR toolchain generates implementation artifacts under `impl/`.
3. A **build receipt** is produced, capturing hashes, toolchain metadata, and signatures.

At runtime, **only capsules with matching receipts are admitted**. The spec remains the source of truth; implementation is a cached derivative.

### 2.4 Determinism and Trust Tiers

All capsules carry explicit determinism and trust metadata in their manifests:

- **Determinism tier** – e.g. `D0_bit_exact`, `D1_numerically_stable`, `D2_soft_deterministic`, `NX_experimental`.
- **Governance tier** – e.g. `core`, `platform`, `extension`, `experimental`, `local`.
- **Trust zone** – e.g. `system`, `tenant`, `session`, `ephemeral`.

The runtime uses these fields to decide:

- Which capsules may participate in critical data paths.
- Which capsules must run in stricter sandboxes.
- Which capsules are eligible for AI-driven composition without human approval.

### 2.5 AI-First, Human-Readable

VNES is designed to be **operated by AI** while remaining **auditable by humans**:

- Every capsule is self-describing with rich docs and schemas.
- Vector embeddings support AI discovery and composition.
- Receipts, policies, and manifests are compact, human-readable documents.

The goal is that an AI planner can assemble and adapt complex pipelines, while a human operator can always inspect **what was used**, **why**, and **under which guarantees**.

---

## 3. Capsule Taxonomy and Namespaces

### 3.1 Capsule IDs

Capsules are identified by a stable, hierarchical ID:

- Pattern: `domain.subdomain.name` (version is a separate field).
- Example: `hypersync.core.geometry.poincare_disk`.

Namespaces typically follow this structure:

- `hypersync.core.*` – Core, highly trusted building blocks.
- `hypersync.platform.*` – Platform features (TUI, audio, routing, telemetry).
- `hypersync.contrib.*` – Community or tenant-contributed capsules.
- `tenant.<slug>.*` – Per-tenant capsules.
- `user.<slug>.*` – Personal or ephemeral capsules.

### 3.2 Capsule Types (Conceptual)

Each capsule declares a `type` in its manifest. Common types include:

- `logic` – Single-algorithm units (e.g., solvers, filters, transforms).
- `pipeline` – Orchestration of other capsules into a reusable flow.
- `ui` – TUI layouts, style themes, projection rules, raster strategies.
- `dataset` – Curated datasets with schemas and provenance.
- `driver` – Adapters for external systems.
- `policy` – Governance and constraints.
- `test` – Validation suites and golden vectors.

The type informs the runtime which interfaces and capabilities to expect.

---

## 4. VNES Architecture and Data Flows

```mermaid
graph TD
    A[Users / AI Agents] -->|Intents & Queries| B[VNES Orchestrator]
    B -->|Semantic & Faceted Query| C[Capsule Registry]
    C -->|Capsule IDs & Manifests| D[VNES Runtime Kernel]
    D -->|Load, Verify, Sandbox| E[Active Capsules]

    subgraph "Active Capsules"
    E1[Core Geometry]:::core
    E2[Consensus Engine]:::core
    E3[TUI & Audio Capsules]:::ui
    E4[User Strategies]:::ext
    E5[Diagnostics & Tests]:::diag
    end

    E -->|Events| F[Event Bus]
    E -->|Reads / Writes| G[State Store]
    E -->|Telemetry & Receipts| H[Observability Plane]

    classDef core fill=#1f6feb,stroke=#0d1117,color=#ffff;
    classDef ui fill=#9e6ffe,stroke=#0d1117,color=#ffff;
    classDef ext fill=#2ea043,stroke=#0d1117,color=#ffff;
    classDef diag fill=#f85149,stroke=#0d1117,color=#ffff;
```

### 4.1 Orchestrator and Registry

The **VNES Orchestrator**:

- Interprets high-level intents (from humans or AI) into concrete capsule plans.
- Delegates discovery to the Registry, which uses embeddings and filters.
- Applies governance and determinism constraints to candidate sets.

The **Capsule Registry** is a content-addressable index that stores:

- Manifests and specs.
- Receipts and build metadata.
- Vector embeddings and search indexes.

### 4.2 Runtime Kernel and Active Capsules

The **VNES Runtime Kernel** is the minimal, trusted core that:

- Loads and verifies capsules against their receipts.
- Constructs per-capsule sandboxes based on `type`, `governance`, and `trust_zone`.
- Manages lifecycle (init/start/stop/suspend) and dependency injection.

### 4.3 Event Bus and State Store

- The **Event Bus** is the primary communication fabric between capsules.
  - Topics are versioned and schema-bound.
  - Deterministic ordering is guaranteed per-topic (at least for D0/D1 capsules).

- The **State Store** maintains shared, transactional state:
  - Ownership is capsule-scoped and governed by manifest declarations.
  - All writes are versioned for time-travel debugging and replay.

---

## 5. Execution Models

VNES supports multiple execution models under the same abstraction:

1. **Ephemeral pipelines** – Short-lived graphs assembled on demand by AI agents.
2. **Long-running services** – Daemons (e.g., solvers, routers) that subscribe to topics.
3. **Batch jobs** – Offline or nearline processing with rich receipts.
4. **Interactive UI flows** – TUI and audio capsules driven by user sessions.

All models:

- Use the same manifest and receipt structures.
- Are discoverable and composable via the same vector-native registry.
- Emit telemetry that can be reasoned about and replayed.

---

## 6. Multi-Tenant and Multi-Environment Operation

VNES is designed for:

- **Single-node developer setups** – All capsules loaded from local directories.
- **Clustered deployments** – Capsules placed across nodes by the scheduler.
- **Multi-tenant SaaS** – Tenant-specific namespaces and governance tiers.

Environment-specific concerns (e.g., GPU availability, bandwidth constraints) are captured via manifest `runtime` and `capabilities` metadata. The runtime uses these to:

- Decide where a capsule may execute.
- Enforce resource ceilings and isolation boundaries.
- Shape scheduling and placement decisions.

---

## 7. Determinism, Governance, and Explainability

Because capsules carry explicit determinism and governance metadata, VNES can:

- Enforce that **critical paths** only contain capsules at or above a required determinism tier.
- Restrict AI-driven composition to vetted capsule sets.
- Generate rich **receipts** that trace which capsules ran, under which policies, and with which results.

This is the foundation for HyperSync's ability to **"show its work"**: every behavior is a composition of auditable, receipt-backed capsules that can be inspected, replayed, and reasoned about by both humans and AI.