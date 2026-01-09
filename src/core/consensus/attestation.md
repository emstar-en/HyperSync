# Consensus Attestation

## Consensus & Attestation System

Configure consensus mechanisms and attestation protocols for nodes and deployments.

### Available Consensus Mechanisms

- **BFT** (Byzantine Fault Tolerance) - PRO tier
- **Raft** - CORE tier
- **Quorum Voting** - CORE tier
- **Threshold Consensus** - CORE tier
- **Unanimous Agreement** - CORE tier
- **Transfinite Consensus** - QM Imperium tier

### Available Attestation Protocols

- **Geometric Proof** - PRO tier
- **Receipt Attestation** - CORE tier
- **Digital Signature** - CORE tier
- **Merkle Tree** - PRO tier
- **Zero-Knowledge Proof** - QM Campaign tier
- **TPM Attestation** - PRO tier

### Quick Start

```bash
# List available mechanisms
hypersync consensus list

# Apply BFT consensus to stack
hypersync consensus apply \
 --target-type stack \
 --target-id stack-abc123 \
 --mechanism mech-bft \
 --quorum 4 \
 --threshold 0.67

# List attestation protocols
hypersync attestation list

# Apply geometric proof attestation
hypersync attestation apply \
 --target-type deployment \
 --target-id deploy-abc123 \
 --protocol proto-geometric \
 --level high \
 --interval 3600

# View configurations
hypersync consensus show --target-type stack --target-id stack-abc123
hypersync attestation show --target-type deployment --target-id deploy-abc123
```

### Use Cases

- Multi-node consensus for model ensembles
- Cross-network consensus via federation
- Cryptographic attestation for compliance
- Receipt-based proof of execution
- Hardware-based attestation (TPM)
- Privacy-preserving attestation (ZK-proofs)

See `spec-pack/docs/consensus/README.md` for complete documentation.