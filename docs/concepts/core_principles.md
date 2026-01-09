# Core Design Principles

## 1. Geometry First
The geometry engine is not a visualization tool; it is the **database**.
-   **Principle**: "If you move the point, you change the state."
-   **Implication**: All business logic is implemented as geometric transformations (rotation, translation, scaling).

## 2. Deterministic Execution
Given the same initial state and the same inputs, the system must reach the *exact* same end state, down to the last bit.
-   **No `time.now()`**: Use logical clocks or block heights.
-   **No `random()`**: Use seeded PRNGs based on state hashes.

## 3. Receipt-Based Architecture
Trust but verify.
-   **Principle**: "No Receipt, No Service."
-   **Implication**: Every API call returns a `Receipt` object containing a cryptographic proof of the operation's validity.

## 4. Tiered Consensus
One size does not fit all.
-   **Tier 1 (Atomic)**: Fast, local, optimistic.
-   **Tier 2 (Sector)**: Regional, robust.
-   **Tier 3 (Global)**: Slow, absolute, expensive.
