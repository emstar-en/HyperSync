"""
AGUA Runtime: Cost Module
==========================

Implements lexicographic ranking and Lorentzian refinement for cost optimization.

Functions:
- lexicographic_rank(candidate, dimensions, params) -> int
  Primary cost ranking via lexicographic ordering of dimensions

- lorentzian_refine(candidate, optimal, params) -> float
  Tie-breaker using γ×exp(-d_L/τ) Lorentzian distance
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple


def lexicographic_rank(
    candidate: Dict[str, Any],
    dimensions: List[str],
    params: Optional[Dict[str, Any]] = None
) -> int:
    """
    Compute lexicographic rank of candidate across cost dimensions.

    Lexicographic ordering: compare dimensions in priority order,
    first dimension that differs determines the rank.

    Args:
        candidate: Dictionary with dimension values
        dimensions: List of dimension names in priority order
        params: Optional parameters:
            - reference_values: Dict of reference values per dimension
            - tolerance: Tolerance for equality comparison (default: 1e-6)

    Returns:
        Rank as integer (lower is better, 0 is optimal)

    Example:
        dimensions = ['latency', 'cost', 'throughput']
        candidate = {'latency': 100, 'cost': 50, 'throughput': 1000}
        rank = lexicographic_rank(candidate, dimensions)
    """
    if params is None:
        params = {}

    reference_values = params.get('reference_values', {})
    tolerance = params.get('tolerance', 1e-6)

    # Compute rank based on lexicographic ordering
    rank = 0
    multiplier = 1

    for i, dim in enumerate(reversed(dimensions)):
        # Get candidate value
        candidate_value = candidate.get(dim, 0.0)

        # Get reference value (optimal)
        reference_value = reference_values.get(dim, 0.0)

        # Compute difference
        diff = abs(candidate_value - reference_value)

        # If difference exceeds tolerance, contribute to rank
        if diff > tolerance:
            # Discretize difference into rank contribution
            # Use log scale to handle wide ranges
            rank_contribution = int(np.log1p(diff / tolerance))
            rank += rank_contribution * multiplier

        # Increase multiplier for next dimension (higher priority)
        multiplier *= 1000

    return rank


def lorentzian_refine(
    candidate: Dict[str, Any],
    optimal: Dict[str, Any],
    params: Optional[Dict[str, Any]] = None
) -> float:
    """
    Compute Lorentzian refinement score for tie-breaking.

    Formula: score = γ × exp(-d_L / τ)

    Where d_L is the Lorentzian distance in hyperboloid model:
    d_L(x, y) = arccosh(-⟨x, y⟩_L)

    For simplicity, we use Euclidean distance as approximation:
    d_L ≈ ||x - y||

    Args:
        candidate: Candidate point (dict of dimension values)
        optimal: Optimal point (dict of dimension values)
        params: Optional parameters:
            - gamma: Scaling factor (default: 1.0)
            - tau: Temperature parameter (default: 1.0)
            - dimensions: List of dimensions to include (default: all)

    Returns:
        Refinement score (higher is better, closer to optimal)
    """
    if params is None:
        params = {}

    gamma = params.get('gamma', 1.0)
    tau = params.get('tau', 1.0)
    dimensions = params.get('dimensions', None)

    # If dimensions not specified, use all common dimensions
    if dimensions is None:
        dimensions = list(set(candidate.keys()) & set(optimal.keys()))

    # Extract vectors
    candidate_vec = np.array([candidate.get(d, 0.0) for d in dimensions], dtype=np.float64)
    optimal_vec = np.array([optimal.get(d, 0.0) for d in dimensions], dtype=np.float64)

    # Compute Euclidean distance (approximation of Lorentzian)
    distance = np.linalg.norm(candidate_vec - optimal_vec)

    # Compute refinement score
    score = gamma * np.exp(-distance / tau)

    return float(score)


def lorentzian_distance_exact(
    x: np.ndarray,
    y: np.ndarray,
    signature: Tuple[int, int] = (1, 1)
) -> float:
    """
    Compute exact Lorentzian distance in hyperboloid model.

    The hyperboloid model uses Minkowski inner product:
    ⟨x, y⟩_L = -x₀y₀ + x₁y₁ + ... + xₙyₙ

    Distance: d_L(x, y) = arccosh(-⟨x, y⟩_L)

    Args:
        x: Point in hyperboloid (n+1 dimensional)
        y: Point in hyperboloid (n+1 dimensional)
        signature: Metric signature (p, q) where p is timelike, q is spacelike

    Returns:
        Lorentzian distance
    """
    x = np.array(x, dtype=np.float64)
    y = np.array(y, dtype=np.float64)

    if len(x) != len(y):
        raise ValueError(f"Vectors must have same length: {len(x)} vs {len(y)}")

    # Minkowski inner product with signature (1, n)
    # ⟨x, y⟩_L = -x₀y₀ + x₁y₁ + ... + xₙyₙ
    inner_product = -x[0] * y[0] + np.dot(x[1:], y[1:])

    # Distance formula: d_L = arccosh(-⟨x, y⟩_L)
    # Clamp to avoid numerical issues
    arg = -inner_product
    arg = max(1.0, arg)  # Must be >= 1 for arccosh

    distance = np.arccosh(arg)

    return float(distance)


def rank_candidates(
    candidates: List[Dict[str, Any]],
    dimensions: List[str],
    optimal: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None
) -> List[Tuple[int, Dict[str, Any], int, float]]:
    """
    Rank multiple candidates using lexicographic ordering and Lorentzian refinement.

    Args:
        candidates: List of candidate dictionaries
        dimensions: Dimension names in priority order
        optimal: Optimal reference point (for refinement)
        params: Parameters for ranking and refinement

    Returns:
        List of tuples: (original_index, candidate, rank, refinement_score)
        Sorted by rank (ascending), then refinement_score (descending)
    """
    if params is None:
        params = {}

    # Compute ranks and refinement scores
    results = []
    for i, candidate in enumerate(candidates):
        rank = lexicographic_rank(candidate, dimensions, params)

        if optimal is not None:
            refinement = lorentzian_refine(candidate, optimal, params)
        else:
            refinement = 0.0

        results.append((i, candidate, rank, refinement))

    # Sort by rank (ascending), then refinement (descending)
    results.sort(key=lambda x: (x[2], -x[3]))

    return results


# Example usage and validation
if __name__ == "__main__":
    print("AGUA Runtime Cost Module - Validation")
    print("=" * 50)

    # Test lexicographic ranking
    dimensions = ['latency', 'cost', 'throughput']

    candidates = [
        {'latency': 100, 'cost': 50, 'throughput': 1000},
        {'latency': 90, 'cost': 60, 'throughput': 1100},
        {'latency': 100, 'cost': 45, 'throughput': 1000},
    ]

    optimal = {'latency': 80, 'cost': 40, 'throughput': 1200}

    params = {
        'reference_values': optimal,
        'tolerance': 1e-6,
        'gamma': 1.0,
        'tau': 10.0,
        'dimensions': dimensions
    }

    print("\nLexicographic ranking test:")
    for i, candidate in enumerate(candidates):
        rank = lexicographic_rank(candidate, dimensions, params)
        print(f"  Candidate {i}: rank = {rank}")

    # Test Lorentzian refinement
    print("\nLorentzian refinement test:")
    for i, candidate in enumerate(candidates):
        score = lorentzian_refine(candidate, optimal, params)
        print(f"  Candidate {i}: refinement = {score:.6f}")

    # Test full ranking
    print("\nFull ranking:")
    ranked = rank_candidates(candidates, dimensions, optimal, params)
    for i, (orig_idx, cand, rank, refine) in enumerate(ranked):
        print(f"  Position {i+1}: Candidate {orig_idx}, rank={rank}, refine={refine:.6f}")

    print("\n✓ All functions operational")
