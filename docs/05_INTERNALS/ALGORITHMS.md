# HyperSync Core Algorithms

This document details the mathematical algorithms driving the Geometry Engine, Consensus mechanisms, and Surreal Number handling.

## 1. Geometric Metrics

### 1.1 Poincaré Distance ($d_{hyp}$)
The fundamental metric for determining "informational distance" between two state vectors $u$ and $v$ in the unit disk ($|u| < 1, |v| < 1$).

**Formula:**
$$ d_{hyp}(u, v) = \text{arccosh} \left( 1 + 2 \frac{||u - v||^2}{(1 - ||u||^2)(1 - ||v||^2)} \right) $$

**Implementation Note:**
- Inputs must be validated to ensure norm < 1.
- For numerical stability near 0, use the expansion $\text{arccosh}(x) = \ln(x + \sqrt{x^2 - 1})$.

### 1.2 Möbius Transformation (State Transition)
To "move" an agent from state $z$ to $z'$ (or to normalize the view such that an agent is at the center), we use Möbius transformations.

**Formula (Translation by $a$):**
$$ T_a(z) = \frac{z - a}{1 - \bar{a}z} $$
- This maps $a$ to the origin $0$.
- Used during **Context Normalization** when an agent needs to evaluate the world from its own perspective.

## 2. Dynamic Positioning Algorithms

### 2.1 Drift Calculation (Entropy Decay)
Agents that are inactive or failing to validate tasks must "drift" towards the edge of the disk (high entropy).

**Algorithm:**
Let $p_t$ be the position at time $t$.
Let $\Delta t$ be the time since last valid transaction.
Let $\vec{r}$ be the radial vector from origin through $p_t$.

$$ p_{t+1} = p_t + \lambda(\Delta t) \cdot \frac{\vec{r}}{||\vec{r}||} $$

Where $\lambda(\Delta t)$ is the drift function:
$$ \lambda(\Delta t) = \alpha \cdot (1 - e^{-\mu \Delta t}) $$
- $\alpha$: Max drift step size.
- $\mu$: Decay rate.

### 2.2 Task Completion (Centering Force)
Upon successful task completion, an agent moves towards the center.

**Algorithm:**
$$ p_{t+1} = p_t - \gamma \cdot p_t $$
- $\gamma$: Centering factor (learning rate), dependent on task difficulty and validation score.

## 3. Spatial Partitioning

### 3.1 Dynamic Voronoi Sectoring
The workspace is partitioned into regions $R_i$ assigned to Coordinators $C_i$.

**Definition:**
A point $x$ belongs to Coordinator $C_i$ if:
$$ d_{hyp}(x, C_i) < d_{hyp}(x, C_j) \quad \forall j \neq i $$

**Re-balancing Trigger:**
If the variance of worker counts across regions exceeds threshold $\sigma^2_{max}$, the Global Planner spawns a new Coordinator at the centroid of the densest region or merges sparse regions.

## 4. Consensus Algorithms

### 4.1 Spatial Quorum Calculation
Determines if a set of agreeing agents $A = \{a_1, ..., a_k\}$ covers sufficient area within a sector $S$.

**Approximation Algorithm:**
1.  **Tessellate** the sector $S$ into a grid of sample points $P = \{p_1, ..., p_N\}$.
2.  **Influence Function:** For each point $p_j$, calculate total influence $I(p_j) = \sum_{a \in A} e^{-d_{hyp}(p_j, a)}$.
3.  **Thresholding:** A point $p_j$ is "covered" if $I(p_j) > \tau$ (influence threshold).
4.  **Coverage Ratio:** $Q = \frac{\text{count(covered points)}}{N}$.
5.  **Decision:** Consensus reached if $Q > Q_{req}$ (e.g., 0.66).

### 4.2 Closest-to-Center Conflict Resolution
Given two conflicting valid transactions $T_A$ (from Agent A) and $T_B$ (from Agent B):

**Logic:**
1.  Calculate $d_A = d_{hyp}(A_{pos}, 0)$.
2.  Calculate $d_B = d_{hyp}(B_{pos}, 0)$.
3.  If $d_A < d_B$, select $T_A$.
4.  If $d_B < d_A$, select $T_B$.
5.  If $d_A == d_B$ (rare), fall back to deterministic hash comparison of Transaction IDs.

### 2.3 Geometric Repulsion (Sybil Defense)
To prevent "Yellow Lane" agents from clustering to manipulate local consensus (Sybil Attack), a repulsion force is applied.

**Formula:**
For two agents $A$ and $B$ with positions $p_A, p_B$:
If $d_{hyp}(p_A, p_B) < \delta_{min}$ (Minimum Separation Distance):

$$ \vec{F}_{rep} = k \cdot \frac{1}{d_{hyp}(p_A, p_B)^2} \cdot \vec{u}_{BA} $$

- $k$: Repulsion constant (defined by Policy Governance).
- $\vec{u}_{BA}$: Unit vector pointing from $B$ to $A$ (in hyperbolic tangent space).

**Effect:**
The Coordinator calculates this force and adds a "Forced Drift" vector to the agent's next position update:
$$ p_{A, t+1} = \text{Möbius}(p_{A, t}, \vec{F}_{rep} \cdot \Delta t) $$

## 5. Surreal Numerics & Infinitary Logic

### 5.1 Conway Cut Construction
Used for representing infinite priorities and infinitesimal costs.

**Definition:**
A surreal number $x$ is defined by two sets of previously created numbers, $L$ (Left) and $R$ (Right), such that no member of $L$ is greater than or equal to any member of $R$.
$$ x = \{ L | R \} $$

### 5.2 Infinitary Comparison
For handling system-critical interrupts ($\omega$) vs user tasks (finite).

**Algorithm:**
To compare $x = \{ X_L | X_R \}$ and $y = \{ Y_L | Y_R \}$:
1.  $x \le y$ if and only if:
    -   There is no $x_L \in X_L$ such that $x_L \ge y$.
    -   There is no $y_R \in Y_R$ such that $y_R \le x$.

**Application:**
-   **Priority Queue:** $P_{sys} = \omega$ (Infinite), $P_{user} \in \mathbb{R}$ (Finite).
-   Since $\omega > n$ for all $n \in \mathbb{R}$, system tasks always preempt user tasks.

### 5.3 Dyadic Approximation (Optimization)
For standard operations, we map finite surreal numbers to dyadic rationals to avoid the overhead of recursive set comparison.

**Mapping:**
$$ x \approx \frac{m}{2^n} $$
-   Used when $x$ is known to be finite and non-infinitesimal.
-   Fallback to full Conway Cut logic when operations involve $\omega$ or $\epsilon$.
