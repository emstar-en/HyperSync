# HyperSync Threat Model & Security Architecture

## 1. Core Security Philosophy
HyperSync operates on a **"Trust but Verify"** model, augmented by **Geometric Isolation**.
- **Verification:** Cryptographic receipts (STUNIR) prove the provenance of code.
- **Isolation:** Unverified code is geometrically and resource-constrained (Sandboxed).
- **Determinism:** Security is not just about access, but about *predictability*. Non-deterministic behavior is treated as a security violation.

## 2. Trust Zones & Boundaries

### Zone 0: The Kernel (Green Lane)
- **Definition:** The VNES Runtime, Geometry Engine, and Consensus Core.
- **Trust Level:** Absolute.
- **Requirements:** Must have valid STUNIR receipts signed by the System Key.
- **Privileges:** Direct memory access, raw socket access, consensus voting.

### Zone 1: Verified Extensions (Green Lane)
- **Definition:** Official or audited 3rd-party capsules.
- **Trust Level:** High.
- **Requirements:** Valid STUNIR receipts signed by a Trusted Vendor.
- **Privileges:** Can participate in D(0) logic, but run in process-isolated sandboxes.

### Zone 2: Unverified / User Space (Yellow Lane)
- **Definition:** User scripts, rapid prototypes, ad-hoc adapters.
- **Trust Level:** Low (Zero Trust).
- **Requirements:** Valid `manifest.json`. No receipt required.
- **Privileges:**
    - **Strict Sandboxing:** No filesystem write access (except temp), no network (except whitelisted).
    - **D(1)/D(2) Only:** Cannot touch bit-exact state directly.
    - **Observer Only:** Cannot vote in consensus.

## 3. Specific Threat Vectors

### A. Capsule Masquerading
**Threat:** A malicious capsule claims to be "Geometry Engine v2.0" to hijack routing.
**Mitigation:**
- **Receipt Validation:** The kernel checks the `impl_hash` against the signed receipt.
- **Namespace Reservation:** `hypersync.core.*` is reserved and requires System Key signatures.

### B. Determinism Drift Attacks
**Threat:** A capsule behaves deterministically during testing but introduces subtle floating-point errors (drift) during runtime to fork the consensus.
**Mitigation:**
- **Runtime Monitoring:** The kernel periodically cross-checks D(0) outputs against redundant execution.
- **Receipt Binding:** The receipt guarantees the code hasn't changed since the audit.

### C. Geometric Sybil Attacks
**Threat:** An attacker spawns thousands of "Yellow Lane" agents to cluster around a specific coordinate and monopolize local resources.
**Mitigation:**
- **Cost of Position:** Occupying high-value coordinates (near origin) requires Proof-of-Work or Token Stake.
- **Repulsion Fields:** The Geometry Engine enforces minimum separation distances between unverified nodes.

### D. Resource Exhaustion (The "Infinite Loop" Attack)
**Threat:** A user script enters an infinite loop or allocates massive memory.
**Mitigation:**
- **Gas Metering / Timeouts:** Yellow Lane capsules have strict CPU time slices.
- **Memory Hard Limits:** Cgroups/WASM limits enforce max RAM usage.

## 4. Data Protection

### At Rest
- **Manifests & Specs:** Stored as plain text (transparency).
- **Private Keys:** Never stored on disk unencrypted. Use HSM or Enclave where possible.
- **State Store:** Merkle-DAG structure ensures tamper-evidence.

### In Transit
- **Inter-Node:** mTLS using ephemeral certificates derived from Node Identity.
- **Inter-Capsule:** Zero-copy shared memory (for Green Lane) or serialized IPC (for Yellow Lane).

## 5. Incident Response
In the event of a detected breach or consensus failure:
1.  **Freeze:** The Geometry Engine halts state transitions.
2.  **Isolate:** The offending capsule is moved to a "Quarantine Manifold" (infinite distance).
3.  **Rollback:** State is reverted to the last known valid checkpoint (proven by receipts).
