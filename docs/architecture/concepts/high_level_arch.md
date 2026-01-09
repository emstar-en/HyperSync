# High-Level System Architecture (Capsule-Based)

## Architecture Overview

HyperSync is composed of modular, self-contained units called **Capsules**.
These capsules interact through strict, schema-validated interfaces and are orchestrated by the **Core Trinity**.

## Block Diagram

```mermaid
graph TD
    User[User / External System] --> Bridge[hypersync.bridge.api]

    subgraph "Core Trinity"
        Env[hypersync.core.environment]
        Geo[hypersync.core.geometry]
        Cons[hypersync.core.consensus]
    end

    subgraph "Inhabitants"
        Agent[hypersync.agent.standard]
    end

    Bridge --> Env
    Env --> Geo
    Env --> Cons
    Env --> Agent

    Agent -.-> Env : Action Request
    Env -.-> Agent : Tick Result
```

## Core Capsules

### 1. Bridge (`hypersync.bridge.api`)
The **Boundary Gateway**.
- **Role**: Secure entry point for REST, WebSocket, and gRPC.
- **Responsibility**: Authentication, Protocol Translation, Traffic Shaping.
- **Determinism**: D2 (Statistical).

### 2. Environment (`hypersync.core.environment`)
The **Simulation Container**.
- **Role**: The "World" that holds all state.
- **Responsibility**: Tick orchestration, Entity management, Timekeeping.
- **Determinism**: D1 (Platform Agnostic).

### 3. Geometry (`hypersync.core.geometry`)
The **Physics Engine**.
- **Role**: The "Space" where entities exist.
- **Responsibility**: Poincaré disk calculations, Distance metrics, Spatial queries.
- **Determinism**: D0 (Bitwise Strict).

### 4. Consensus (`hypersync.core.consensus`)
The **Truth Engine**.
- **Role**: The "Judge" of state transitions.
- **Responsibility**: Conflict resolution, Ordering, Validity checks.
- **Determinism**: D0 (Bitwise Strict).

### 5. Standard Agent (`hypersync.agent.standard`)
The **Inhabitant**.
- **Role**: The "Actor" (User or AI).
- **Responsibility**: Sensing, Decision making, Action proposal.
- **Determinism**: D1 (Shell) / D2 (Brain).
