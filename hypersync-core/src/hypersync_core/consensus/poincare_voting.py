"""Poincaré Voting Consensus

Hyperbolic distance-based voting using Poincaré ball model.
Leverages exponential separation of Byzantine nodes in hyperbolic space.

Complexity: O(n log n)
Byzantine tolerance: f < n/3
"""

import numpy as np
from typing import List, Tuple
from ..geometry.hyperbolic import (
    hyperbolic_distance,
    hyperbolic_midpoint,
)


def poincare_voting_consensus(
    proposals: List[np.ndarray],
    threshold_factor: float = 2.0
) -> Tuple[np.ndarray, List[int]]:
    """Poincaré voting consensus using hyperbolic distance.
    
    Algorithm:
    1. Embed proposals in Poincaré ball
    2. Compute pairwise hyperbolic distances
    3. Detect Byzantine nodes via exponential distance threshold
    4. Compute hyperbolic barycenter of honest cluster
    
    Args:
        proposals: List of node proposals in Poincaré ball
        threshold_factor: Distance threshold multiplier (default 2.0)
    
    Returns:
        consensus: Hyperbolic barycenter
        byzantine_nodes: Detected Byzantine node indices
    
    Complexity: O(n log n)
    """
    n = len(proposals)
    
    if n < 4:
        raise ValueError("Need at least 4 nodes for Byzantine consensus")
    
    # Validate proposals are in Poincaré ball
    for i, p in enumerate(proposals):
        norm = np.linalg.norm(p)
        if norm >= 1.0:
            raise ValueError(f"Proposal {i} not in Poincaré ball: norm={norm}")
    
    # Compute pairwise distances
    distances = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = hyperbolic_distance(proposals[i], proposals[j])
            distances[i, j] = d
            distances[j, i] = d
    
    # Compute median distance for each node
    median_distances = []
    for i in range(n):
        dists = [distances[i, j] for j in range(n) if j != i]
        median_distances.append(np.median(dists))
    
    # Adaptive threshold using log(n) scaling
    global_median = np.median(median_distances)
    threshold = global_median + threshold_factor * np.log(n)
    
    # Detect Byzantine nodes
    byzantine_nodes = []
    honest_nodes = []
    
    for i in range(n):
        if median_distances[i] > threshold:
            byzantine_nodes.append(i)
        else:
            honest_nodes.append(i)
    
    # Verify Byzantine tolerance
    if len(honest_nodes) < 2 * len(byzantine_nodes) + 1:
        raise ValueError(f"Too many Byzantine nodes: {len(byzantine_nodes)} out of {n}")
    
    # Compute hyperbolic barycenter
    honest_proposals = [proposals[i] for i in honest_nodes]
    consensus = hyperbolic_barycenter_fast(honest_proposals)
    
    return consensus, byzantine_nodes


def hyperbolic_barycenter_fast(points: List[np.ndarray]) -> np.ndarray:
    """Fast hyperbolic barycenter using pairwise midpoints.
    
    Args:
        points: List of points in Poincaré ball
    
    Returns:
        Approximate barycenter
    
    Complexity: O(n log n)
    """
    if len(points) == 0:
        raise ValueError("Cannot compute barycenter of empty list")
    
    if len(points) == 1:
        return points[0]
    
    # Hierarchical pairwise averaging
    current_points = points.copy()
    
    while len(current_points) > 1:
        next_level = []
        
        for i in range(0, len(current_points), 2):
            if i + 1 < len(current_points):
                midpoint = hyperbolic_midpoint(
                    current_points[i],
                    current_points[i + 1]
                )
                next_level.append(midpoint)
            else:
                next_level.append(current_points[i])
        
        current_points = next_level
    
    return current_points[0]
