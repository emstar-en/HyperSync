# Geometric Retrieval Pipeline Specification

## 1. Overview
The retrieval pipeline is designed to find geometric entities (agents, tasks, data points) relevant to a query vector $q$ in the Poincaré disk. It uses a two-stage architecture to balance speed and precision.

## 2. Stage 1: Coarse Retrieval (IVF-PQ)
**Goal**: Rapidly filter the dataset from $N$ items to a candidate set $M$ (where $M \ll N$).
**Method**: Inverted File with Product Quantization (IVF-PQ) adapted for approximate hyperbolic proximity.

*   **Index Structure**:
    *   **Voronoi Cells**: The space is divided into $k$ Voronoi cells based on centroids.
    *   **Quantization**: Vectors are compressed using Product Quantization (sub-space clustering).
*   **Parameters**:
    *   `nlist` (Number of Cells): $pprox 4 \sqrt{N}$
    *   `nprobe` (Cells to Search): $10-20$ (Tunable for Recall vs. Latency)
    *   `code_size`: 16 bytes per vector.
*   **Metric**: Approximated Euclidean distance on the disk representation (fast but slightly distorted).

## 3. Stage 2: Intrinsic Reranking
**Goal**: Re-order the candidate set $M$ using exact hyperbolic geometry.
**Method**: Brute-force calculation of Poincaré distance on the small candidate set.

*   **Input**: Query $q$, Candidate Set $M = \{x_1, ..., x_m\}$.
*   **Algorithm**:
    For each $x_i \in M$:
    1.  **Decompress**: Reconstruct $x_i$ from PQ codes (or fetch full vector if cached).
    2.  **Exact Distance**: Calculate $d_{\mathbb{D}}(q, x_i) = 	ext{arccosh}\left(1 + rac{2|q - x_i|^2}{(1-|q|^2)(1-|x_i|^2)}ight)$.
    3.  **Curvature Adjustment**: If local curvature $\kappa 
eq -1$, scale distance: $d' = d / \sqrt{|\kappa|}$.
*   **Output**: Top-$K$ items with smallest $d'$.

## 4. Query Execution Flow
1.  **Query Vectorization**: User query $	o$ Embedding $	o$ Projection to $\mathbb{D}$.
2.  **IVF Search**: Identify nearest Voronoi centroids. Scan `nprobe` lists.
3.  **Candidate Collection**: Gather top $M$ candidates (e.g., $M = 10 \cdot K$).
4.  **Rerank**: Compute exact hyperbolic distances. Sort.
5.  **Filter**: Apply Access Control (ACL) and Policy filters.
6.  **Return**: Top-$K$ results.

## 5. Performance Targets
*   **Latency (p95)**: < 50ms for $N=10^6$.
*   **Recall@10**: > 0.95 (Stage 1 must not miss true neighbors).
*   **Throughput**: > 1000 QPS per node.
