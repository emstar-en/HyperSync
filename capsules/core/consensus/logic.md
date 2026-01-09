# Consensus & Attestation Capsule

## Description
The Consensus & Attestation Capsule provides a robust framework for managing consensus mechanisms and attestation protocols within the HyperSync ecosystem. It enables the definition, configuration, and application of various consensus strategies and verification methods to different targets (e.g., nodes, networks, data streams).

## Components

### Consensus Manager
The Consensus Manager is responsible for the lifecycle of consensus mechanisms. It allows for:
- **Creation**: Defining new consensus mechanisms with specific parameters and tier requirements.
- **Retrieval**: Fetching details of existing mechanisms.
- **Application**: Applying a specific consensus mechanism to a target (e.g., a specific network segment).
- **Configuration**: Managing the active configuration of consensus for targets.

### Attestation Manager
The Attestation Manager handles verification and proof protocols. It supports:
- **Protocol Definition**: Creating attestation protocols with defined verification levels and cryptographic requirements.
- **Application**: Enforcing attestation protocols on targets.
- **Receipt Management**: Tracking attestation receipts (though primarily handled by the Receipts subsystem, this manager configures the requirements).

## Data Models

### ConsensusMechanism
Defines a strategy for achieving consensus.
- `mechanism_id`: Unique identifier.
- `mechanism_type`: Type of consensus (e.g., "poh", "pbft").
- `tier_requirements`: Requirements for nodes participating in this mechanism.

### AttestationProtocol
Defines a method for verifying data or state.
- `protocol_id`: Unique identifier.
- `protocol_type`: Type of attestation (e.g., "zk-snark", "merkle-proof").
- `verification`: Configuration for the verification process.

### ConsensusConfiguration & AttestationConfiguration
Represent the active application of a mechanism or protocol to a specific target.

## Usage
This capsule is intended to be used by the Core system to enforce network integrity and agreement. It interacts with the underlying SQLite database to persist configurations and state.
