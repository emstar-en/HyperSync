# HyperSync Synchronization

## Synchronization Mechanisms
HyperSync abandons the "one-size-fits-all" consensus model in favor of a spatially-aware, multi-tiered approach. This ensures that local, low-risk operations are fast, while global, critical operations remain secure.

> **Detailed Mechanics:** For a comprehensive guide on the Tiered Consensus model, Spatial Quorums, and Conflict Resolution, please refer to [Consensus Mechanics](../../07_documentation/human/mechanics/consensus_mechanics.md).

## Consensus Tiers

### Tier 1: Local Consensus (Neighborhood)
- **Scope**: Immediate geometric neighbors.
- **Mechanism**: Optimistic execution with neighbor validation.
- **Latency**: Ultra-low.
- **Use Case**: Logging, minor state updates, ephemeral data.

### Tier 2: Regional Consensus (Sector)
- **Scope**: A defined geometric sector (Voronoi region).
- **Mechanism**: Geometrically-weighted PBFT.
- **Latency**: Medium.
- **Use Case**: Standard transactions, resource allocation, task handoffs.

### Tier 3: Global Consensus (Network)
- **Scope**: The entire HyperSync network.
- **Mechanism**: Full state validation and cryptographic proof.
- **Latency**: High.
- **Use Case**: Protocol upgrades, global configuration changes, security lockdowns.

## Geometric Consensus
- **Spatial Quorums**: Consensus is reached when a sufficient *area* of the state space is covered by agreeing agents, not just a count of nodes.
- **Closest-to-Center Rule**: In the event of a conflict, the agent geometrically closer to the center (0,0) is prioritized.
