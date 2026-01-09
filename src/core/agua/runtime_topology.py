"""
AGUA Runtime: Topology Module
==============================

Computes topological invariants for architecture quality assessment.

Functions:
- beta0_quality(graph, params) -> int
  Counts connected components (β₀) in architecture graph
"""

import numpy as np
from typing import Dict, Any, List, Set, Optional, Tuple
from collections import deque


def beta0_quality(
    graph: Dict[str, Any],
    params: Optional[Dict[str, Any]] = None
) -> int:
    """
    Compute β₀ (beta-zero) topological invariant.

    β₀ counts the number of connected components in the graph.
    Lower β₀ indicates better connectivity (fewer isolated components).

    Args:
        graph: Graph specification with:
            - nodes: List of node identifiers
            - edges: List of [source, target] pairs
        params: Optional parameters (reserved for future use)

    Returns:
        Number of connected components (β₀)

    Example:
        graph = {
            'nodes': ['A', 'B', 'C', 'D'],
            'edges': [['A', 'B'], ['C', 'D']]
        }
        beta0 = beta0_quality(graph)  # Returns 2 (two components: A-B and C-D)
    """
    if params is None:
        params = {}

    nodes = graph.get('nodes', [])
    edges = graph.get('edges', [])

    if not nodes:
        return 0

    # Build adjacency list
    adjacency = {node: [] for node in nodes}

    for edge in edges:
        if len(edge) != 2:
            continue
        source, target = edge

        # Add both directions for undirected graph
        if source in adjacency:
            adjacency[source].append(target)
        if target in adjacency:
            adjacency[target].append(source)

    # Count connected components using BFS
    visited = set()
    num_components = 0

    for node in nodes:
        if node not in visited:
            # Start new component
            num_components += 1

            # BFS to mark all nodes in this component
            queue = deque([node])
            visited.add(node)

            while queue:
                current = queue.popleft()

                for neighbor in adjacency.get(current, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

    return num_components


def compute_betti_numbers(
    graph: Dict[str, Any],
    max_dimension: int = 1
) -> List[int]:
    """
    Compute Betti numbers up to specified dimension.

    Betti numbers are topological invariants:
    - β₀: Number of connected components
    - β₁: Number of 1-dimensional holes (cycles)
    - β₂: Number of 2-dimensional voids

    Args:
        graph: Graph specification
        max_dimension: Maximum dimension to compute (default: 1)

    Returns:
        List of Betti numbers [β₀, β₁, ...]
    """
    betti = []

    # β₀: Connected components
    beta0 = beta0_quality(graph)
    betti.append(beta0)

    if max_dimension >= 1:
        # β₁: Number of independent cycles
        beta1 = _compute_beta1(graph)
        betti.append(beta1)

    return betti


def _compute_beta1(graph: Dict[str, Any]) -> int:
    """
    Compute β₁ (number of independent cycles).

    Uses formula: β₁ = |E| - |V| + β₀
    where |E| is number of edges, |V| is number of vertices.
    """
    nodes = graph.get('nodes', [])
    edges = graph.get('edges', [])

    num_vertices = len(nodes)
    num_edges = len(edges)
    beta0 = beta0_quality(graph)

    # Euler characteristic: χ = V - E
    # For graphs: β₁ = E - V + β₀
    beta1 = num_edges - num_vertices + beta0

    # β₁ cannot be negative
    beta1 = max(0, beta1)

    return beta1


def graph_quality_score(
    graph: Dict[str, Any],
    params: Optional[Dict[str, Any]] = None
) -> float:
    """
    Compute overall graph quality score based on topology.

    Lower score is better (fewer components, simpler topology).

    Args:
        graph: Graph specification
        params: Optional parameters:
            - beta0_weight: Weight for β₀ (default: 1.0)
            - beta1_weight: Weight for β₁ (default: 0.5)
            - target_beta0: Target number of components (default: 1)

    Returns:
        Quality score (lower is better)
    """
    if params is None:
        params = {}

    beta0_weight = params.get('beta0_weight', 1.0)
    beta1_weight = params.get('beta1_weight', 0.5)
    target_beta0 = params.get('target_beta0', 1)

    # Compute Betti numbers
    betti = compute_betti_numbers(graph, max_dimension=1)
    beta0 = betti[0]
    beta1 = betti[1] if len(betti) > 1 else 0

    # Penalize deviation from target β₀
    beta0_penalty = abs(beta0 - target_beta0)

    # Penalize cycles (β₁)
    beta1_penalty = beta1

    # Combined score
    score = beta0_weight * beta0_penalty + beta1_weight * beta1_penalty

    return float(score)


def analyze_graph_topology(
    graph: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Comprehensive topological analysis of graph.

    Args:
        graph: Graph specification

    Returns:
        Analysis results with:
        - beta0: Number of connected components
        - beta1: Number of independent cycles
        - num_nodes: Number of nodes
        - num_edges: Number of edges
        - quality_score: Overall quality score
        - components: List of component node sets
    """
    nodes = graph.get('nodes', [])
    edges = graph.get('edges', [])

    # Compute Betti numbers
    betti = compute_betti_numbers(graph, max_dimension=1)
    beta0 = betti[0]
    beta1 = betti[1] if len(betti) > 1 else 0

    # Compute quality score
    quality = graph_quality_score(graph)

    # Find components
    components = _find_components(graph)

    return {
        'beta0': beta0,
        'beta1': beta1,
        'num_nodes': len(nodes),
        'num_edges': len(edges),
        'quality_score': quality,
        'components': components,
        'num_components': len(components)
    }


def _find_components(graph: Dict[str, Any]) -> List[Set[str]]:
    """
    Find all connected components in graph.

    Returns:
        List of sets, each containing nodes in a component
    """
    nodes = graph.get('nodes', [])
    edges = graph.get('edges', [])

    # Build adjacency list
    adjacency = {node: [] for node in nodes}

    for edge in edges:
        if len(edge) != 2:
            continue
        source, target = edge

        if source in adjacency:
            adjacency[source].append(target)
        if target in adjacency:
            adjacency[target].append(source)

    # Find components
    visited = set()
    components = []

    for node in nodes:
        if node not in visited:
            # BFS to find component
            component = set()
            queue = deque([node])
            visited.add(node)
            component.add(node)

            while queue:
                current = queue.popleft()

                for neighbor in adjacency.get(current, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        component.add(neighbor)
                        queue.append(neighbor)

            components.append(component)

    return components


# Example usage and validation
if __name__ == "__main__":
    print("AGUA Runtime Topology Module - Validation")
    print("=" * 50)

    # Test 1: Single connected component
    print("\nTest 1: Single connected component")
    graph1 = {
        'nodes': ['A', 'B', 'C', 'D'],
        'edges': [['A', 'B'], ['B', 'C'], ['C', 'D']]
    }

    beta0 = beta0_quality(graph1)
    print(f"  Graph: {graph1['nodes']}")
    print(f"  Edges: {graph1['edges']}")
    print(f"  β₀ = {beta0} (expected: 1)")

    # Test 2: Two disconnected components
    print("\nTest 2: Two disconnected components")
    graph2 = {
        'nodes': ['A', 'B', 'C', 'D'],
        'edges': [['A', 'B'], ['C', 'D']]
    }

    beta0 = beta0_quality(graph2)
    print(f"  Graph: {graph2['nodes']}")
    print(f"  Edges: {graph2['edges']}")
    print(f"  β₀ = {beta0} (expected: 2)")

    # Test 3: Graph with cycle
    print("\nTest 3: Graph with cycle")
    graph3 = {
        'nodes': ['A', 'B', 'C'],
        'edges': [['A', 'B'], ['B', 'C'], ['C', 'A']]
    }

    betti = compute_betti_numbers(graph3, max_dimension=1)
    print(f"  Graph: {graph3['nodes']}")
    print(f"  Edges: {graph3['edges']}")
    print(f"  β₀ = {betti[0]} (expected: 1)")
    print(f"  β₁ = {betti[1]} (expected: 1)")

    # Test 4: Comprehensive analysis
    print("\nTest 4: Comprehensive analysis")
    analysis = analyze_graph_topology(graph2)
    print(f"  β₀ = {analysis['beta0']}")
    print(f"  β₁ = {analysis['beta1']}")
    print(f"  Quality score = {analysis['quality_score']:.2f}")
    print(f"  Components: {analysis['num_components']}")

    print("\n✓ All functions operational")
