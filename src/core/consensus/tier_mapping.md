# Consensus Tier Mapping

# Consensus-Tier Mapping

## Overview

This patch establishes the foundational mapping between HyperSync's 14 consensus mechanisms and 7 service tiers. The mapping follows a resource-based allocation philosophy where heavier, more complex mechanisms are reserved for higher tiers, while simpler, more efficient mechanisms are available across all tiers.

## Philosophy

### Core Principles

1. **Installation-based Enforcement**
 - Users only receive consensus mechanisms installed for their tier
 - No runtime checks needed - clean and secure
 - Prevents tier violations at the package level

2. **Resource-based Allocation**
 - Lightweight mechanisms → available to more tiers
 - Heavy mechanisms → reserved for higher tiers
 - Aligns with tier resource budgets (CPU, memory, GPU)

3. **Attestation Alignment**
 - Lower tiers have minimal attestation overhead
 - Higher tiers require stronger validation
 - Matches operational security requirements

4. **Safety-first Approach**
 - Even CORE tier gets Simple BFT
 - Critical for robotics and safety-critical applications
 - Responsible deployment model

5. **Simplicity Scales Down**
 - Basic mechanisms available to all
 - Advanced features require higher tiers
 - Progressive capability enhancement

## Tier Structure

### CORE (Tier 1)
**Use Case:** Home labs, OSS, development, robotics prototyping

**Mechanisms (5):**
- Gossip Protocol - Event propagation
- Vector Clock - Causality tracking
- CRDT - Conflict-free replication
- Merkle Tree - Data integrity
- Simple BFT - Safety-critical applications ⚠️

**Resources:**
- Nodes: 8
- Dimensions: 12
- Memory: 512 MB
- GPU: Not required

**Attestation:** oss_minimal

---

### Basic (Tier 2)
**Use Case:** Small production deployments

**Mechanisms (7):** All CORE +
- Quorum-based - Simple voting
- Raft - Leader election

**Resources:**
- Nodes: 12
- Dimensions: 12
- Memory: 2 GB
- GPU: Optional (400ms budget)

**Attestation:** client_banking

---

### PRO (Tier 3)
**Use Case:** Professional production deployments

**Mechanisms (9):** All Basic +
- Paxos - Robust consensus
- Proof of Stake - Energy-efficient validation

**Resources:**
- Nodes: 24
- Dimensions: 32
- Memory: 2 GB
- GPU: Optional (400ms budget)

**Attestation:** operator_confidence

**Features:** Release channels, registry (lite/full)

---

### Advanced (Tier 4)
**Use Case:** Enterprise deployments, unlimited nodes

**Mechanisms (12):** All PRO +
- Byzantine Fault Tolerant (BFT) - Full Byzantine protection
- Tendermint - Modern BFT with finality
- HotStuff - Optimized BFT for large networks

**Resources:**
- Nodes: Unlimited
- Dimensions: 32 (soft max 64)
- Memory: 2 GB
- GPU: Optional (400ms budget)

**Attestation:** axiomatic_operator (keyring required)

**Features:** Geodesic routing, encrypted export

---

### QM Venture (Tier 5)
**Use Case:** Quantum-grade venture tier

**Mechanisms (14):** All Advanced +
- Riemannian Barycenter - Geometric consensus on manifolds
- Geometric Consensus - Full geometric synchronization

**Resources:**
- Nodes: Unlimited
- Dimensions: 32 (soft max 64)
- Memory: 2 GB
- GPU: **Required** (500ms budget, 8GB VRAM)

**Attestation:** enterprise_enhanced (keyring + multi-sig)

**Features:** Full geometric consensus capabilities

---

### QM Campaign (Tier 6)
**Use Case:** Large-scale quantum operations

**Mechanisms (14):** Same as QM Venture

**Resources:**
- Nodes: Unlimited
- Dimensions: 32 (soft max 64)
- Memory: 4 GB
- GPU: **Required** (600ms budget, 8GB VRAM)

**Attestation:** enterprise_strong (keyring + multi-sig)

---

### QM Imperium (Tier 7)
**Use Case:** Maximum security deployments

**Mechanisms (14):** Same as QM Venture

**Resources:**
- Nodes: Unlimited
- Dimensions: 32 (soft max 64)
- Memory: 2 GB
- GPU: **Required** (400ms budget, 8GB VRAM)
- **HSM Required**

**Attestation:** enterprise_strict (keyring + multi-sig + HSM)

## Files in This Patch

### Core Mapping Files
- `consensus/tier_mapping.json` - Master tier-to-mechanism mapping
- `consensus/mechanism_profiles.json` - Resource profiles for all 14 mechanisms
- `consensus/tier_capabilities.json` - Capability matrix per tier

### Installation Manifests
- `consensus/installation_manifests/core_manifest.json`
- `consensus/installation_manifests/basic_manifest.json`
- `consensus/installation_manifests/pro_manifest.json`
- `consensus/installation_manifests/advanced_manifest.json`
- `consensus/installation_manifests/qm_venture_manifest.json`
- `consensus/installation_manifests/qm_campaign_manifest.json`
- `consensus/installation_manifests/qm_imperium_manifest.json`

### Schemas
- `schemas/consensus_tier_mapping.schema.json` - Validation schema for tier mappings
- `schemas/mechanism_profile.schema.json` - Validation schema for mechanism profiles

## Integration Points

This patch integrates with:
- `planner/routing/hypersync_routing.tiers.json` - Existing tier definitions
- `schemas/consensus.schema.json` - Existing consensus schemas
- `schemas/consensus_validation.schema.json` - Existing validation schemas

## Mechanism Summary

| Weight | Mechanisms | Tiers |
|--------|-----------|-------|
| Lightweight | Gossip, Vector Clock, CRDT, Merkle Tree | CORE+ |
| Light | Simple BFT, Quorum-based | CORE+, Basic+ |
| Moderate | Raft, Paxos, Proof of Stake | Basic+, PRO+ |
| Heavy | BFT, Tendermint, HotStuff | Advanced+ |
| Very Heavy | Riemannian Barycenter, Geometric Consensus | QM tiers only |

## Safety-Critical Note

⚠️ **Simple BFT in CORE Tier**

The CORE tier includes Simple BFT specifically for safety-critical applications like robotics. This ensures that even home lab deployments have access to Byzantine fault tolerance when needed for safety, demonstrating responsible engineering practices.

## Next Steps

This system provides- **:** User-facing APIs for consensus selection
- **:** CLI commands for consensus management
- **:** Configuration schemas and defaults
- **:** Documentation and examples

## Version

- **Version:** 1.0.0
- **Created:** 2025-11-18T09:41:53.811191
- **Status:** Foundation Complete

---

*Part of the HyperSync Consensus-Tier Integration Series*