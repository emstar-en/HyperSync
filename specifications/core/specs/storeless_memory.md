# Storeless Memory & State Reconstruction

## 1. Core Concept
"Storeless Memory" is a storage optimization strategy where the system persists minimal full state snapshots ("Anchors") and reconstructs intermediate states on-demand using a chain of geometric transformations ("Deltas"). This leverages the deterministic nature of the Geometry Engine.

*   **Philosophy**: Store the *path* (transformations), not just the *destinations* (states).
*   **Benefit**: Reduces storage footprint by 90%+ for high-frequency consensus logs.

## 2. Data Structures

### 2.1 Memory Anchor ($A_t$)
A full, materialized snapshot of the system state at time $t$.
*   **Schema**:
    *   `timestamp`: $t$
    *   `state_vector`: Full vector $z \in \mathbb{D}^n$
    *   `hash`: Merkle root of the state
    *   `checkpoint_id`: Unique UUID

### 2.2 Memory Delta ($\Delta_{t 	o t+1}$)
A lightweight record of the transformation applied to transition from $t$ to $t+1$.
*   **Schema**:
    *   `parent_hash`: Hash of state at $t$
    *   `transform_op`: The Möbius transformation $M \in SU(1,1)$ or update vector.
    *   `parameters`: $\{ 	heta, a, b \}$ (Rotation, Translation parameters)
    *   `signature`: Cryptographic proof of the transition.

## 3. Reconstruction Logic
To retrieve state $S_{target}$:
1.  **Find Anchor**: Locate the nearest preceding anchor $A_{base}$ where $t_{base} \le t_{target}$.
2.  **Fetch Chain**: Retrieve the sequence of deltas $[\Delta_1, \Delta_2, ..., \Delta_k]$ connecting $t_{base}$ to $t_{target}$.
3.  **Replay**:
    $$ S_{current} = A_{base} $$
    $$ 	ext{for } \Delta 	ext{ in chain}: S_{current} = 	ext{Apply}(\Delta, S_{current}) $$
4.  **Verify**: Check if `Hash(S_{current})` matches the expected state hash (if known).

## 4. Promotion & Demotion Policies

### 4.1 Promotion (Materialization)
Converting a computed state into a stored Anchor.
*   **Trigger**: Chain length $> 100$ deltas.
*   **Trigger**: Access frequency $> 50$ reads/minute (Hot State).
*   **Action**: Serialize $S_{current}$ to disk as a new Anchor.

### 4.2 Demotion (Pruning)
Removing an Anchor and replacing it with a Delta chain from a previous Anchor.
*   **Trigger**: Access frequency $< 1$ read/hour (Cold State).
*   **Condition**: A valid path exists from a previous Anchor.
*   **Action**: Delete Anchor blob, ensure Delta chain integrity.
