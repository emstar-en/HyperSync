# Ledger Compaction Invariants

## 1. Goal
To reduce the storage size of the consensus ledger and state history without compromising cryptographic integrity, auditability, or geometric causality.

## 2. Preservation Guarantees (Invariants)
Any compaction operation must strictly adhere to the following invariants. Violation results in a `CorruptedHistoryError`.

### 2.1 Causal Chain Integrity
*   **Invariant**: The cryptographic hash chain must remain unbroken.
*   **Requirement**: If a sequence of blocks $[B_i, ..., B_j]$ is compacted into a summary block $B_{sum}$, then:
    $$ 	ext{Verify}(B_{sum}, 	ext{PrevHash}=B_{i-1}.	ext{Hash}) 	o 	ext{True} $$
    $$ B_{sum}.	ext{Hash} \equiv 	ext{MerkleRoot}([B_i, ..., B_j]) $$

### 2.2 Geometric Homotopy
*   **Invariant**: The simplified trajectory of an agent must be homotopic to the original trajectory (continuously deformable without crossing obstacles).
*   **Requirement**: The compacted path cannot pass through "Forbidden Zones" (e.g., high-security enclaves) that the original path avoided.

### 2.3 State Reachability
*   **Invariant**: Any historical state $S_t$ must be reconstructible within a bounded time.
*   **Requirement**: Maximum distance from any timestamp $t$ to the nearest Anchor $A$ must not exceed $K_{max}$ deltas (e.g., $K_{max} = 1000$).

## 3. Compaction Strategies

### 3.1 Hyperbolic Ramer-Douglas-Peucker (RDP)
Used for simplifying geometric trajectories (paths of agents).
*   **Algorithm**:
    1.  Select start point $P_1$ and end point $P_n$.
    2.  Find point $P_k$ with maximum *perpendicular hyperbolic distance* to the geodesic segment $\gamma(P_1, P_n)$.
    3.  If $dist(P_k, \gamma) > \epsilon$ (tolerance), keep $P_k$ and recurse on sub-segments.
    4.  Else, discard intermediate points.
*   **Result**: A sparse set of points approximating the curve within error $\epsilon$.

### 3.2 Snapshot Pruning
Used for state history.
*   **Logic**:
    *   Keep Anchors at major epochs (e.g., every 1 hour).
    *   Keep Deltas for all transitions.
    *   Discard intermediate "Snapshot" blobs between Anchors (rely on Delta replay).

## 4. Compaction Triggers
*   **Time-Based**: Run nightly on logs older than 24 hours.
*   **Size-Based**: Trigger when ledger size > 10 GB.
*   **Event-Based**: Trigger after a "Global Consensus" checkpoint is finalized.
