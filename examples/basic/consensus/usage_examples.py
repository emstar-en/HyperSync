"""Consensus & Attestation Usage Examples"""
from hypersync.consensus import ConsensusAttestationManager

manager = ConsensusAttestationManager()

# Example 1: List available mechanisms
print("=== Available Consensus Mechanisms ===")
mechanisms = manager.list_consensus_mechanisms()
for mech in mechanisms:
    tier = mech.tier_requirements.get("min_tier", "N/A") if mech.tier_requirements else "N/A"
    print(f"{mech.name} ({mech.mechanism_type}) - Min Tier: {tier}")

# Example 2: Apply BFT consensus to stack
print("\n=== Apply BFT Consensus ===")
consensus_config = manager.apply_consensus(
    target_type="stack",
    target_id="stack-abc123",
    mechanism_id="mech-bft",
    parameters={"quorum_size": 4, "threshold": 0.67},
    nodes=["node-1", "node-2", "node-3", "node-4"]
)
print(f"Applied: {consensus_config.config_id}")
print(f"Mechanism: {consensus_config.mechanism_id}")
print(f"Nodes: {len(consensus_config.nodes)}")

# Example 3: List attestation protocols
print("\n=== Available Attestation Protocols ===")
protocols = manager.list_attestation_protocols()
for proto in protocols:
    tier = proto.tier_requirements.get("min_tier", "N/A") if proto.tier_requirements else "N/A"
    verif = proto.verification.get("verification_level", "N/A") if proto.verification else "N/A"
    print(f"{proto.name} ({proto.protocol_type}) - Tier: {tier}, Level: {verif}")

# Example 4: Apply geometric proof attestation
print("\n=== Apply Geometric Proof Attestation ===")
attest_config = manager.apply_attestation(
    target_type="deployment",
    target_id="deploy-abc123",
    protocol_id="proto-geometric",
    verification_level="high",
    attestation_frequency={"interval_seconds": 3600}
)
print(f"Applied: {attest_config.config_id}")
print(f"Protocol: {attest_config.protocol_id}")
print(f"Verification Level: {attest_config.verification_level}")

# Example 5: Get consensus configuration
print("\n=== Get Consensus Configuration ===")
config = manager.get_consensus_config("stack", "stack-abc123")
if config:
    print(f"Config ID: {config.config_id}")
    print(f"Mechanism: {config.mechanism_id}")
    print(f"Status: {config.status}")
    print(f"Parameters: {config.parameters}")

# Example 6: Get attestation configuration
print("\n=== Get Attestation Configuration ===")
config = manager.get_attestation_config("deployment", "deploy-abc123")
if config:
    print(f"Config ID: {config.config_id}")
    print(f"Protocol: {config.protocol_id}")
    print(f"Verification Level: {config.verification_level}")
    print(f"Receipts: {len(config.receipts) if config.receipts else 0}")

# Example 7: Apply consensus to assembly
print("\n=== Apply Raft Consensus to Assembly ===")
consensus_config = manager.apply_consensus(
    target_type="assembly",
    target_id="assembly-xyz789",
    mechanism_id="mech-raft",
    parameters={"quorum_size": 3, "timeout_seconds": 5},
    nodes=["node-a", "node-b", "node-c"]
)
print(f"Applied Raft consensus: {consensus_config.config_id}")

# Example 8: Apply signature attestation to node
print("\n=== Apply Signature Attestation to Node ===")
attest_config = manager.apply_attestation(
    target_type="node",
    target_id="node-xyz789",
    protocol_id="proto-signature",
    verification_level="cryptographic",
    attestation_frequency={"interval_seconds": 1800}
)
print(f"Applied signature attestation: {attest_config.config_id}")

print("\n=== All Examples Complete ===")
