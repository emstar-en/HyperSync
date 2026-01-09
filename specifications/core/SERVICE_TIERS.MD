# HyperSync Service Tiers

HyperSync operates on a Dual-Licensing Model to ensure sustainability while maintaining a robust open-source foundation.

## 1. Core (Open Source)
**License:** AGPLv3
**Target:** Hobbyists, Students, Open Source Contributors.
**Philosophy:** "The Engine is Free."

### Features
- **Routing Attestation:** Standard.
- **ICO Probe Access:** Conditional. Requires `AttestationValidationReceipt` and `SignatureReceipt` (Proof of Work/Identity) for every probe.
- **VNES Libraries:** Essential.
- **Consensus:** Basic geometric and standard algorithms (Gossip, Merkle Tree, Simple BFT).
- **Hosting:** Self-hosted only.

### Included Capsules
- `hypersync.core.geometry`
- `hypersync.core.logic`
- `hypersync.core.kernel`
- `hypersync.core.io.basic`
- `hypersync.core.bridge.uplink`
- `hypersync.core.factory`
- `hypersync.core.catalogue`

---

## 2. Basic (Commercial)
**License:** Commercial Subscription
**Target:** Individual Power Users, Freelancers.
**Philosophy:** "Convenience and Standard Tools."

### Features
- **Routing Attestation:** Priority.
- **ICO Probe Access:** Unconditional. Direct access without per-probe receipts (frictionless).
- **VNES Libraries:** Essential + Standard.
- **Consensus:** Core + Quorum, Raft, and more advanced geometric algorithms.
- **Hosting:** Cloud hosting available.

### Included Capsules (Everything in Core plus...)
- `hypersync.std.io.extended`
- `hypersync.std.data.processing`
- `hypersync.std.agents.basic`
- `hypersync.std.network.http`
- `hypersync.ui.tui.base`
- `hypersync.ui.dashboard`
- `hypersync.ui.console`
- `hypersync.ui.visualizer`

---

## 3. Pro (Commercial)
**License:** Commercial Subscription
**Target:** Startups, Small Teams.
**Philosophy:** "Advanced Capabilities and Collaboration."

### Features
- **Routing Attestation:** Priority.
- **ICO Probe Access:** Unconditional.
- **VNES Libraries:** Essential + Standard + Advanced.
- **Consensus:** Basic + Paxos, Proof of Stake, and advanced spectral/kahler geometry algorithms.
- **Hosting:** Cloud hosting + Team Tools.
- **ZK Capabilities:** Recursive Proving.

### Included Capsules (Everything in Basic plus...)
- `hypersync.adv.coordination`
- `hypersync.adv.ai.reasoning`
- `hypersync.adv.physics.simulation`
- `hypersync.adv.security.crypto`

---

## 4. Advanced (Commercial)
**License:** Commercial Subscription
**Target:** Large Enterprises.
**Philosophy:** "Scale and Security."

### Features
- **Routing Attestation:** Dedicated.
- **ICO Probe Access:** Unconditional.
- **VNES Libraries:** All + Enterprise Suite.
- **Consensus:** Full suite including Tendermint, HotStuff, and exotic geometric BFTs.
- **Hosting:** SLA Support, Audit Logs.

### Included Capsules
- Everything in Pro.
- Enterprise Suite (Custom integrations, not listed in standard catalogue).

---

## 5. Quartermaster (Partner)
**License:** Partner Agreement
**Target:** Regulated Industries, Government.
**Philosophy:** "Managed Trust."

### Features
- **Routing Attestation:** Managed.
- **ICO Probe Access:** Unconditional.
- **VNES Libraries:** All + Enterprise Suite.
- **Consensus:** Full suite + Experimental/Research algorithms.
- **Hosting:** White-glove managed deployment.

### Included Capsules
- Everything in Advanced.
- Bespoke/Research Capsules.
