# HyperSync VNES Extensibility Protocol

## Philosophy
HyperSync is designed to be "infinitely extensible" through the **Vector-Native Execution System (VNES)**. Every extension—whether a solver, a UI widget, or a psychological model—must be encapsulated as a **VNES Capsule**.

## The VNES Contract
For a component to function as a native part of the program, it must adhere to the following contract:

### 1. Everything is a Capsule
Extensions are not just code; they are **Capsules**.
*   **Manifest**: Must provide a `manifest.json` defining capabilities, governance tier, and resource requirements.
*   **Spec**: Must provide a `spec/` directory with logic and schema definitions.
*   **Receipts**: Must emit **VNES Receipts** (cryptographic proofs of execution) for every operation.

### 2. The Universal Wrapper (VNES Adapter)
Legacy code or external libraries must be wrapped in a **VNES Adapter**.
*   **Input**: Accepts VNES Tensors (Geometry-aware data).
*   **Process**: Executes the external logic (e.g., a Python script, a C++ solver).
*   **Output**: Returns a VNES Receipt and a Result Tensor.

### 3. Geometric Registration
Components register into the **Geometric Lattice**, not just a list.
*   *Registration*: `Registry.register(capsule=MyCapsule, coordinates=...)`
*   *Discovery*: Agents discover capabilities by traversing the geometry (e.g., "Find nearest solver for optimization").

## Extension Types

### A. Solvers & Operators
*   Must implement the `vnes.execute` interface.
*   Must provide a `determinism_tier` (e.g., `D1_numerically_stable`).

### B. UI & Visualization
*   Must accept `UGEO` (Universal Geometry) data.
*   Must render to the **Universal Viewport**.

### C. Cognitive & Psychological Models
*   See **Psychometric Tensor Specification**.
*   Psychological states are mapped to geometric coordinates (e.g., "Confusion" = High Entropy/Drift).

## Implementation Strategy
To "build in what must be", the Factory automatically wraps generated code in VNES Capsules.
