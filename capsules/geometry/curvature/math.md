# Curvature Dynamics & Ricci Flow

## 1. Ricci Flow Equation
**Definition**: The metric tensor $g_{ij}$ evolves under Ricci flow to smooth out irregularities in the network topology.

**Equation**:
$$ \frac{\partial g_{ij}}{\partial t} = -2 R_{ij} $$
where $R_{ij}$ is the Ricci curvature tensor.

## 2. Discrete Curvature
**Definition**: On a discrete graph $G=(V, E)$, we use Ollivier-Ricci curvature.

**Logic**:
$$ \kappa(x, y) = 1 - \frac{W_1(m_x, m_y)}{d(x, y)} $$
where $W_1$ is the Wasserstein distance between probability measures $m_x$ and $m_y$ around nodes $x$ and $y$.

## 3. Topology Optimization
**Mechanism**:
- Edges with negative curvature $\kappa(x, y) < 0$ are "bottlenecks" and candidates for reinforcement.
- Edges with positive curvature are well-connected.
