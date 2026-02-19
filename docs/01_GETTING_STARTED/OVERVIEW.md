# HyperSync System Overview

**Version:** 2.0.0
**Status:** Production Specification

## 1. Architecture

HyperSync is a distributed orchestration system composed of three main layers:

### 1.1 The Geometry Engine (The Physics)
The core kernel that defines the "Space" in which agents operate. It calculates positions, distances, and trajectories on the Poincaré disk.

### 1.2 The Consensus Layer (The Law)
A tiered consensus mechanism that validates state transitions. It ensures that all agents agree on the "Truth" of the system state.

### 1.3 The Agent Layer (The Actors)
Autonomous units of logic (Coordinators, Workers, Policy Agents) that perform the actual work.

## 2. Capsule-Based Architecture

HyperSync is built upon a **Capsule Architecture**. The system is not a monolithic binary but a collection of self-contained, strictly specified units called **Capsules**.

- **Capsules** define *Logic*, *Schema*, and *Policy* in a language-agnostic format.
- **STUNIR** (the compiler) consumes these capsules to generate the executable runtime.
- **The Core Trinity** (Environment, Geometry, Consensus) are simply the first three capsules that bootstrap the universe.

For detailed specifications, see [Capsule Specification](../11_VNES/CAPSULE_SPEC.md).

## 3. Core Capabilities

- **Geometric Orchestration**: Embeds services and workloads into **non-Euclidean geometric spaces** (primarily hyperbolic) to drive placement and routing.
- **Deterministic Execution**: Enforces behavior under clearly defined deterministic rules.

For a full list of capabilities, see [Capabilities](../10_REFERENCE/CAPABILITIES.md).

## 4. Subsystems

### 4.1 VNES (Vector Native Extension System)
VNES is a **Token-Efficiency Subsystem** for AI Agents. It provides a library of **Capsules**—pre-computed, deterministic blocks of logic and data.

For more details, see [VNES Overview](../11_VNES/VNES_OVERVIEW.md).

### 4.2 HVS-NVM (HyperVisor System - Node Virtual Machine)
The HVS-NVM system provides persistent, geometry-aware vector storage that can be attached to models, stacks, trunks, or networks.

For more details, see [HVS-NVM Overview](../04_COMPONENTS/HVS_NVM.md).
