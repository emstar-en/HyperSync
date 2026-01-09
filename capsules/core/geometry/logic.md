# HyperSync Core Geometry Capsules d Logic Specification (Enhanced)

## 1. Purpose and Scope

The **HyperSync Core Geometry** capsule family (`hypersync.core.geometry.*`) provides deterministic geometric services used to:

- Define and query **virtual spaces** for environment virtualization.
- Support **routing**, **partitioning**, and **load distribution** across nodes and tenants.
- Drive **visualizations** and **diagnostics** in TUI and other surfaces.
- Serve as the geometric substrate for **consensus** and **safety mechanisms**.

These capsules must support **bit-exact determinism (D0_bit_exact)** for core operations and remain stable across builds, platforms, and deployments.

---

## 2. Conceptual Model

### 2.1 Spaces, Manifolds, and Charts

The geometry subsystem models environments as **spaces**:

- A **Space** is a named, versioned, and typed geometric domain (e.g., Euclidean, hyperbolic, product spaces).  
- A **Manifold** is a collection of local charts with transition functions.  
- A **Chart** provides coordinate mappings between local and global representations.

Each space is identified by a `space_id` and a `space_version`, and is defined by a configuration:

- Metric type (e.g., Euclidean, Poincar, Klein).  
- Dimensionality.  
- Curvature parameters.  
- Topology (e.g., bounded/unbounded, periodic boundaries).

### 2.2 Virtualization and Safe Fencing

Geometry provides **fences** and **regions** that bound AI-visible environments:

- **Regions of Interest (ROIs)** define subspaces where AI agents operate.  
- **Safety Fences** mark boundaries beyond which agents cannot propose actions.

These concepts allow HyperSync to:

- Present AI agents with a rich but **bounded and controlled world**.  
- Ensure that routing and consensus live within predictable geometric limits.  
- Encode isolation between tenants, sessions, or experiments in geometric form.

---

## 3. Core Operations and APIs

The geometry capsules expose a set of **deterministic operations** over spaces and points. All operations:

- Are pure functions of their inputs (no hidden global state).  
- Return structured results plus diagnostics and metadata.  
- Emit receipts for critical operations when requested.

### 3.1 Space Introspection

- `GetSpaceDescriptor(space_id)`  
  Returns a complete descriptor of the space, including metric, dimensionality, curvature, and fences.

- `ListSpaces(filter)`  
  Enumerates available spaces (e.g., per-tenant, per-environment) with metadata.

### 3.2 Metric Operations

- `Distance(space_id, point_a, point_b, options)`  
  Computes the distance between two points under the space's metric.

- `Norm(space_id, vector, options)`  
  Computes the norm of a vector at a point or in a tangent space.

### 3.3 Geodesics and Paths

- `Geodesic(space_id, point_start, point_end, options)`  
  Returns a discretized geodesic path and its properties (length, curvature).

- `ShortestPath(space_id, source, targets, constraints)`  
  Computes shortest paths over a discrete or continuous structure embedded in the space.

### 3.4 Projections and Embeddings

- `Project(space_id, point, target_chart)`  
  Converts a point between charts within a manifold.

- `Embed(space_id, external_descriptor)`  
  Embeds external entities (nodes, tasks, data shards) into the space as points or regions.

### 3.5 Safety and Fencing Operations

- `IsInsideFence(space_id, point, fence_id)`  
  Returns whether a point lies inside a defined safety fence.

- `ClampToFence(space_id, point, fence_id)`  
  Projects a point to the nearest safe point on or within a fence.

These operations are used by higher-level capsules (routing, consensus, environment controllers) to ensure that AI agents and workloads operate **within safe, well-defined regions**.

---

## 4. Determinism and Numerical Stability

### 4.1 Determinism Tier

Core geometry capsules declare `determinism_tier = D0_bit_exact` for their primary operations:

- Given identical inputs (including configuration and tolerance parameters), they must produce **bit-identical outputs**.  
- Randomized algorithms (if any) must be avoided or replaced with deterministic equivalents.  
- Platform-specific differences (e.g., floating-point behavior) must be controlled via:
  - Fixed-precision arithmetic where necessary.  
  - Reference implementations with conformance tests.

### 4.2 Tolerances and Approximations

Where approximations are unavoidable (e.g., iterative solvers), the spec must:

- Declare convergence criteria and error bounds.  
- Encode tolerances explicitly in the schema and in receipts.  
- Provide conformance tests that assert acceptable ranges.

---

## 5. Receipts and Telemetry

Geometry operations that materially affect environment structure or routing can emit **geometry receipts** containing:

- Space ID and version.  
- Operation name and parameters (or hashes thereof).  
- Result hashes and key scalar values (e.g., distances, lengths).  
- Determinism tier and tolerance parameters.  
- Capsule ID, version, and manifest hash.

These receipts support:

- **Time-travel debugging** for routing and consensus issues.  
- **Conformance checking** across nodes or implementations.  
- **Explainability** for humans (e.g., why an AI agent saw a particular layout or route).

---

## 6. Security, Environment Virtualization, and AI Containment

The geometry capsules participate directly in environment virtualization and AI containment:

- Geometry defines **which regions exist** and **how they connect**.  
- Environment capsules consume geometry descriptors to construct AI-visible environments.  
- Safety fences and ROIs prevent AI from acting outside allowed subspaces.

Policy (see `capsules_hypersync.core.geometry_spec_policy.ENHANCED.yaml`) enforces that:

- Geometry capsules run in a **system trust zone** with strict sandboxes.  
- They do not initiate network connections or external side effects.  
- Only authorized capsules (e.g., environment managers, consensus) can modify space configurations.

This ensures that the **shape of the world** seen by AI agents is itself a deterministic, auditable artifact of HyperSync's core.
