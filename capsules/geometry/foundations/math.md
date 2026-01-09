# Geometry Foundations: Hyperbolic Manifolds

## 1. Metric Space
**Definition**: The system operates on a hyperbolic manifold $\mathbb{H}^n$ with constant negative curvature $K = -1$.

**Distance Metric**:
The distance $d(x, y)$ between two points $x, y \in \mathbb{H}^n$ in the Poincaré ball model is given by:
$$ d(x, y) = \text{arccosh} \left( 1 + \frac{2 \|x - y\|^2}{(1 - \|x\|^2)(1 - \|y\|^2)} \right) $$

## 2. Geodesics
**Definition**: Geodesics are the shortest paths between points. In the Poincaré ball, they are circular arcs orthogonal to the boundary sphere $S^{n-1}$.

**Equation**:
For points $u, v$, the geodesic $\gamma(t)$ satisfies $\nabla_{\dot{\gamma}} \dot{\gamma} = 0$.

## 3. Embedding Optimization
**Logic**:
Nodes are embedded into $\mathbb{H}^n$ to minimize the distortion between network latency and hyperbolic distance.

**Objective Function**:
We minimize the stress function $S$:
$$ S = \sum_{i<j} \left( \frac{d_{\mathbb{H}}(x_i, x_j) - \delta_{ij}}{\delta_{ij}} \right)^2 $$
Where:
- $d_{\mathbb{H}}(x_i, x_j)$ is the hyperbolic distance between node embeddings.
- $\delta_{ij}$ is the measured network latency (or graph distance) between nodes $i$ and $j$.

**Update Rule**:
Embeddings are updated via Riemannian Gradient Descent (RGD):
$$ x_i^{(t+1)} = \text{exp}_{x_i^{(t)}} (-\eta \nabla_{x_i} S) $$
