# Consensus Capsule: Geometric Agreement

## Description
The Consensus Capsule encapsulates the logic for achieving state agreement across the distributed HyperSync network. It utilizes a geometry-aware consensus mechanism where "truth" is determined by the spatial alignment of nodes (Spatial Quorums).

## Components

### Consensus Engine
The core driver that processes incoming transactions and drives them to finality.
- **Responsibilities**:
    - Transaction Validation (Signature & Payload).
    - Quorum Formation (Geometric grouping).
    - Entropy Monitoring (System stability).

## Key Metrics
- **Global Entropy**: A measure of disorder in the network state. Lower is better.
- **Average Drift**: The divergence of local clocks/states from the geometric mean.
- **Spatial Quorums**: The number of active geometric consensus groups.

## Usage
This capsule is used by the `ConsensusRouter` to process API requests. It provides the underlying state machine for the consensus layer.
