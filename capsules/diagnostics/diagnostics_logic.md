# Fault Detection Logic & Mathematical Foundations

## 1. D0 Violation (Determinism)
**Definition**: A D0 violation occurs when the local execution state hash $H(S_{local})$ differs from the consensus state hash $H(S_{consensus})$.

**Logic**:
$$ \delta_{D0} = \begin{cases} 1 & \text{if } H(S_{local}) \neq H(S_{consensus}) \\ 0 & \text{if } H(S_{local}) = H(S_{consensus}) \end{cases} $$

**Mechanism**:
- Compute SHA-256 hash of the serialized state vector at the end of each transaction $t$.
- Compare with the aggregated signature threshold from the consensus quorum.

## 2. D1 Violation (Statistical Consistency)
**Definition**: A D1 violation occurs when the scalar output $O_{local}$ deviates from the consensus mean $\mu_{consensus}$ by more than the allowed epsilon $\epsilon$.

**Logic**:
$$ \delta_{D1} = \begin{cases} 1 & \text{if } |O_{local} - \mu_{consensus}| > \epsilon \\ 0 & \text{if } |O_{local} - \mu_{consensus}| \leq \epsilon \end{cases} $$

**Mechanism**:
- Calculate Euclidean distance for vector outputs or absolute difference for scalar outputs.
- $\epsilon$ is defined in `determinism_tiers.json`.

## 3. Liveness Failure
**Definition**: A node $N$ is considered dead if the time since the last valid heartbeat $T_{last}$ exceeds the threshold $T_{timeout}$.

**Logic**:
$$ \delta_{Liveness} = \begin{cases} 1 & \text{if } (T_{now} - T_{last}) > T_{timeout} \\ 0 & \text{otherwise} \end{cases} $$

**Mechanism**:
- Monotonic clock comparison.

## 4. Integrity Failure
**Definition**: An integrity failure occurs when a cryptographic proof, signature, or receipt fails validation.

**Logic**:
$$ \delta_{Integrity} = \begin{cases} 1 & \text{if } \text{Verify}(\sigma, m, pk) = \text{False} \\ 0 & \text{otherwise} \end{cases} $$

**Mechanism**:
- Ed25519 signature verification on all incoming protocol messages.
- Merkle proof verification for state sync.
