# HyperSync Glossary

### Acceptance Gate
A logic mechanism in the Geometry Engine that validates state transitions based on their geometric cost and drift. Anomalies trigger consensus reconfiguration.

### Agent
Autonomous component that orchestrates operators and manages workflows.

### AGUA
**Automated Geometric Universal Architecture**
- The execution supervision and orchestration layer for HyperSync.
- Enforces **Geometry Control Rulesets** (e.g., curvature bounds) to ensure system stability.
- Operates in modes like Conservative Geometric Core (production) and Exploration & Research.

### AttestationValidationReceipt
A specific receipt type required for Core tier users to access `op://network/ico/probe`.

### Barycenter (Riemannian)
The geometric "center of mass" used to compute consensus in hyperbolic space.

### Build Receipt
Cryptographic record of build process and transformations.

### Canonical Form
Unique, standardized representation of data or specification.

### Capsule Isolation
The mechanism by which VNES capsules are sandboxed, ensuring that a failure in one capsule (e.g., a driver crash) does not destabilize the entire system.

### Conformance Test
Test ensuring implementation adheres to specification requirements.

### Consensus Tiers
A system of 14 consensus mechanisms integrated across service tiers, following the principle of **Installation-based Enforcement** (users only receive mechanisms for their tier).

### Curvature
Measure of how space deviates from Euclidean geometry.

### Determinism Tiers (D-Tiers)
Classification system for execution precision and reproducibility:
- **D0 (Fully Deterministic):** Bit-exact reproducibility required (e.g., financial, crypto).
- **D1 (Statistically Deterministic):** Results within epsilon tolerance (e.g., ML training).
- **D2 (Non-Deterministic):** General-purpose or exploratory tasks.

### Deterministic Transformation
Transformation that always produces the same output for the same input.

### Drift
The tendency of a node or state to diverge from the consensus center. In HyperSync, drift is naturally penalized by the geometry, creating a "gravity" towards agreement.

### Epoch Timestamp
Fixed timestamp used for reproducible builds.

### Exponential Map
The operation that maps a tangent vector at a point on the manifold to a point on the manifold itself (moving "straight" along a geodesic).

### Geodesic
Shortest path between two points in hyperbolic space.

### Geometric Median
The robust consensus point calculated in hyperbolic space, minimizing the sum of geodesic distances to all node proposals.

### Geoticket
A cryptographically signed instruction set for a deterministic path that ignores the manifold geometry (e.g., wormholes/shortcuts).

### Holonomy
The geometric effect where parallel transport along a closed loop results in a rotation, used in HyperSync to detect inconsistencies in distributed state updates.

### HVS
**HyperVisual System**
The core vector communication and collaboration system of HyperSync.
- **Purpose:** Enables direct, efficient "beep-boop" communication between models using vector representations instead of tokenizing to/from human languages (English).
- **Scope:** Inclusive of multiple geometries (hyperbolic, Euclidean, etc.) beyond just storage.
- **Role:** Solves the inefficiency of inter-model communication by providing a native, geometry-aware medium for collaboration.

### HVS Renormalization
The process of re-centering the hyperbolic manifold to prevent floating-point errors during deep traversals.

### Hyperbolic Geometry
Non-Euclidean geometric space used by HyperSync for efficient representation and computation of hierarchical and distributed data structures.

### HyperSync
Geometry-aware orchestration and synchronization system for distributed computational workloads using hyperbolic geometry.

### Logarithmic Map
The inverse of the Exponential Map, mapping a point on the manifold to a tangent vector at a reference point (finding the "direction and distance").

### Manifest
Living document tracking all files, checksums, and metadata in the specification.

### Operator
Atomic computational unit in HyperSync that performs specific transformations or operations.

### PCT
**Pathfinder / Cartographer / Trailblazer**
- The lifecycle framework for developing geometry-aware workflows.
- **Pathfinder:** Exploratory phase (D2 allowed) to discover solution spaces and generate episodes.
- **Cartographer:** Mapping phase (D1/D0) to analyze landscapes and produce uncertainty maps.
- **Trailblazer:** Compilation phase (D0 only) to produce **Canonized Workflows** and deployment artifacts.

### Poincaré Disk
Hyperbolic geometry model used for visualization and computation.

### Policy
Declarative rules governing system behavior, resource allocation, and operational constraints.

### Receipt
Cryptographic proof of computation or transformation, including checksums and transformation chain.

### Regions of Interest (ROIs)
Dynamically allocated subspaces for specific tenants or workloads, isolated by high-curvature "ridges".

### Ricci Flow Optimization
A process used to smooth out irregularities in the manifold metric, optimizing the geometry for more efficient routing and clustering.

### Safety Fences
Geodesic polygons that bound the valid state space for an agent. Attempting to route outside triggers a `GeometricSingularityError`.

### Service Tiers
The tiered access model (Core, Basic, Pro, Advanced, Quartermaster) defining feature sets and licensing (AGPLv3 vs Commercial).

### SignatureReceipt
A specific receipt type required for Core tier users to access `op://network/ico/probe`.

### Single Base Program
Philosophy where the specification is the canonical source of truth, free of build artifacts and patch logs.

### Spec File
Formal specification document defining system behavior or component.

### STUNIR
**Standardization Theorem Unique Normal Intermediate Reference**
- Intermediate representation format ensuring deterministic transformations
- Provides cryptographic proof of transformation correctness
- Enables AI models to show their work and prove non-hallucination

### Vectorization
Process of converting documentation into embeddings for semantic search.

### VNES
**Vector-Native Extension System**
The universal runtime and development plane for HyperSync where all behaviors (logic, UI, drivers, etc.) are treated as **Vector Capsules**.
- **Capsules:** Strongly typed units (Logic, Pipeline, UI, Dataset, Driver, Policy, Test) discoverable via vector search.
- **Vector-Native Discovery:** Capsules are indexed by high-dimensional embeddings for semantic query resolution.
- **Spec-First:** Capsules start as specs, are processed by STUNIR, and must have valid receipts to run.
