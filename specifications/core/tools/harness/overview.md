# HyperSync Test Harness Overview

## Introduction
The HyperSync Test Harness is a specialized framework designed to validate the deterministic properties of the Hyperbolic Geometry Engine and the consensus mechanisms. Unlike standard unit testing frameworks, this harness is "geometry-aware," capable of simulating non-Euclidean spaces and relativistic time dilation effects.

## Core Capabilities

### 1. Geometric Fuzzing
The harness generates random geometric topologies in the Poincaré disk to test edge cases in sectoring and distance calculations.
- **Boundary Testing**: Simulates coordinates near the disk boundary ($|z| \to 1$) to check for floating-point precision errors.
- **Transformation Invariance**: Verifies that Möbius transformations preserve distances and angles.

### 2. Consensus Simulation
Simulates network partitions and latency using a relativistic model.
- **Drift Injection**: Artificially injects clock drift to test the robustness of the `Drift < Max_Drift` acceptance gate.
- **Byzantine Generators**: Spawns worker nodes that intentionally broadcast invalid geometric proofs to test the `Verify(Proof)` gate.

### 3. Determinism Verification
Ensures that given the same initial state $S_0$ and input vector $\vec{I}$, the system always transitions to $S_{n}$.
- **Replayability**: All test runs are seeded and fully replayable.
- **State Hash Checks**: Compares Merkle roots of the state tree at every tick.

## Usage
Run the harness via the CLI:
```bash
hypersync-cli test --suite=geometry --fuzz-factor=0.5
```
