# BFT Consensus Logic & Mathematical Foundations

## 1. Protocol Phases
**Definition**: The consensus protocol proceeds in three phases: Pre-prepare, Prepare, and Commit.

**Logic**:
1.  **Pre-prepare**: Primary broadcasts $\langle \text{PRE-PREPARE}, v, n, d \rangle_{\sigma_p}$.
2.  **Prepare**: Replica $i$ broadcasts $\langle \text{PREPARE}, v, n, d, i \rangle_{\sigma_i}$ upon receiving valid Pre-prepare.
3.  **Commit**: Replica $i$ broadcasts $\langle \text{COMMIT}, v, n, d, i \rangle_{\sigma_i}$ upon collecting $2f+1$ Prepare messages.

## 2. Safety Condition
**Definition**: Two distinct requests cannot be committed for the same sequence number $n$ in the same view $v$.

**Proof**:
Quorum intersection ensures that any two quorums $Q_1, Q_2$ have at least one correct replica in common:
$$ |Q_1 \cap Q_2| \ge f + 1 $$

## 3. View Change
**Definition**: If the primary fails, replicas initiate a view change to $v+1$.

**Logic**:
Trigger condition:
$$ T_{timer} > T_{timeout}(v) $$
New view $v'$ is established when $2f+1$ $\text{VIEW-CHANGE}$ messages are collected.
