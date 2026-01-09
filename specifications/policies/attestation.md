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

- **Geometric Proof** - CORE tier
- **Receipt Attestation** - CORE tier
- **Digital Signature** - CORE tier
- **Merkle Tree** - BASIC tier
- **TPM Attestation** - BASIC tier

### Zero-Knowledge & Providence Levels

Zero-Knowledge (ZK) and Providence features are available across all tiers to ensure verifiable computation.

- **ZK Proving (Standard)** - CORE tier
  - Generate standard proofs for transaction validity and state updates.
  - Includes basic circuit generation and ZK Verification.

- **ZK Proving (Privacy)** - BASIC tier
  - Privacy-preserving computations (shielded transactions).
  - Support for private inputs and witness hiding.

- **ZK Proving (Recursive)** - PRO tier
  - Complex circuit composition.
  - Recursive proofs and Inductive Value Logic (IVC).

- **ZK Proving (Hyperscale)** - ADVANCED tier
  - Fundamental, lightweight ($O(\log n)$) large scale proofs.
  - Optimized for massive state proving and high-throughput verification.

- **ZK Campaign** - QM Campaign tier
  - Large-scale, federated, or Multi-Party Computation (MPC) based proofs.

### Tier-Specific Access Control

Access to sensitive network operations is governed by tier-specific policies to balance security and usability.

#### ICO Probe Access (`op://network/ico/probe`)

- **CORE Tier**: Conditional Access.
  - Access to `op://network/ico/probe` is **conditional**.
  - Requires valid **`AttestationValidationReceipt`** and **`SignatureReceipt`** to be presented with the request.
  - This ensures that Core tier nodes prove their integrity before probing the network.

- **BASIC Tier (and above)**: Unconditional Access.
  - Access to `op://network/ico/probe` is **unconditional**.
  - No specific receipts are required for this operation.
  - This removes friction for paid tiers, assuming a higher level of trust or different billing/verification mechanisms.

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
