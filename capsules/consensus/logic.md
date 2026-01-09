# Consensus Logic & Mathematical Foundations

## 1. Quorum Formation
**Definition**: A valid quorum $Q$ is a subset of the validator set $V$ that meets the Byzantine Fault Tolerance threshold.

**Logic**:
$$ |Q| \ge \lceil \frac{2}{3} |V| + 1 \rceil $$
Where $|V|$ is the total voting power (or count) of active validators.

## 2. Vote Validation
**Definition**: A vote $v_i$ from validator $i$ is valid if it is properly signed and references the correct proposal $P$.

**Logic**:
$$ \text{Valid}(v_i) \iff \text{Verify}(v_i.\text{sig}, v_i.\text{digest}, PK_i) \land v_i.\text{view} == \text{CurrentView} $$

## 3. Commit Rule
**Definition**: A block or state transition is committed when a supermajority of valid votes is aggregated.

**Logic**:
$$ \text{Committed}(P) \iff \sum_{i \in Q} \text{Weight}(i) > \frac{2}{3} \text{TotalWeight} $$
