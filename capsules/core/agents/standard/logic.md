# Standard Agent Capsule: Coordination & Governance

## Description
The Standard Agent Capsule encapsulates the core governance and coordination logic of the HyperSync network. It includes the Policy Governance Agent (Tier 3) and the Coordinator Agent (Tier 2), working together to enforce the AGUA (Adaptive Geometric User Access) protocol and manage trust zones.

## Components

### Policy Governance Agent
The supreme authority for trust and policy within the system.
- **Role**: "Supreme Court" / "Gatekeeper"
- **Responsibilities**:
    - Maintains Constitutional Geometry.
    - Enforces Trust Zones (Kernel, Verified, User).
    - Validates Receipts to determine access lanes (Green vs. Yellow).

### Coordinator Agent
The warden of a specific geometric sector.
- **Role**: Sector Orchestrator
- **Responsibilities**:
    - Manages Worker agents within its sector.
    - Enforces policies dictated by the Policy Governance Agent.
    - Provisions sandboxes for untrusted (Yellow Lane) workers.
    - Assigns tasks based on worker capabilities and trust levels.

## Data Models

### TrustZone
- `ZONE_0` (Kernel): Full access, requires D0 determinism.
- `ZONE_1` (Verified): IPC access, requires D0/D1.
- `ZONE_2` (User): Sandboxed, allows D2.

### DeterminismTier
- `D0`: Bit-Exact.
- `D1`: Statistically Deterministic.
- `D2`: Non-Deterministic.

## Usage
This capsule provides the backbone for secure and organized agent interaction. It ensures that only verified agents can access sensitive system resources.
