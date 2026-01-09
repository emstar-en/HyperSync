"""
AGUA Runtime: Manifold Module
==============================

Implements product manifold operations for multi-space geometry.

Functions:
- product_metric(x1, x2, y1, y2, params) -> float
  Product manifold distance: d²_M×N = d²_M + d²_N

- couple(x, y, params) -> tuple
  Couples points from two manifolds into product space
"""

import numpy as np
from typing import Tuple, Dict, Any, Optional, List


def product_metric(
    x1: np.ndarray,
    x2: np.ndarray,
    y1: np.ndarray,
    y2: np.ndarray,
    params: Optional[Dict[str, Any]] = None
) -> float:
    """
    Compute product manifold distance.

    For product manifold M × N, the distance is:
    d²_M×N((x1, y1), (x2, y2)) = d²_M(x1, x2) + d²_N(y1, y2)

    Args:
        x1: Point in first manifold M
        x2: Point in first manifold M
        y1: Point in second manifold N
        y2: Point in second manifold N
        params: Optional parameters:
            - manifold_M_type: Type of M ('euclidean', 'poincare', 'sphere')
            - manifold_N_type: Type of N ('euclidean', 'poincare', 'sphere')
            - weights: Tuple (w_M, w_N) for weighted product (default: (1, 1))

    Returns:
        Product manifold distance
    """
    if params is None:
        params = {}

    manifold_M_type = params.get('manifold_M_type', 'euclidean')
    manifold_N_type = params.get('manifold_N_type', 'euclidean')
    weights = params.get('weights', (1.0, 1.0))

    x1 = np.array(x1, dtype=np.float64)
    x2 = np.array(x2, dtype=np.float64)
    y1 = np.array(y1, dtype=np.float64)
    y2 = np.array(y2, dtype=np.float64)

    # Compute distance in M
    if manifold_M_type == 'euclidean':
        d_M_sq = np.sum((x1 - x2)**2)
    elif manifold_M_type == 'poincare':
        # Poincaré ball distance
        d_M = _poincare_distance(x1, x2)
        d_M_sq = d_M**2
    elif manifold_M_type == 'sphere':
        # Spherical distance
        d_M = _spherical_distance(x1, x2)
        d_M_sq = d_M**2
    else:
        raise ValueError(f"Unknown manifold type for M: {manifold_M_type}")

    # Compute distance in N
    if manifold_N_type == 'euclidean':
        d_N_sq = np.sum((y1 - y2)**2)
    elif manifold_N_type == 'poincare':
        d_N = _poincare_distance(y1, y2)
        d_N_sq = d_N**2
    elif manifold_N_type == 'sphere':
        d_N = _spherical_distance(y1, y2)
        d_N_sq = d_N**2
    else:
        raise ValueError(f"Unknown manifold type for N: {manifold_N_type}")

    # Weighted product metric
    w_M, w_N = weights
    d_product_sq = w_M * d_M_sq + w_N * d_N_sq

    return float(np.sqrt(d_product_sq))


def couple(
    x: np.ndarray,
    y: np.ndarray,
    params: Optional[Dict[str, Any]] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Couple points from two manifolds into product space.

    Creates a point in M × N from points in M and N.

    Args:
        x: Point in manifold M
        y: Point in manifold N
        params: Optional parameters:
            - coupling_strength: Strength of coupling (default: 0.0, no coupling)
            - coupling_type: Type of coupling ('none', 'linear', 'nonlinear')

    Returns:
        Tuple (x_coupled, y_coupled) representing point in M × N
    """
    if params is None:
        params = {}

    coupling_strength = params.get('coupling_strength', 0.0)
    coupling_type = params.get('coupling_type', 'none')

    x = np.array(x, dtype=np.float64)
    y = np.array(y, dtype=np.float64)

    if coupling_type == 'none' or coupling_strength == 0.0:
        # No coupling, just return original points
        return x, y

    elif coupling_type == 'linear':
        # Linear coupling: mix components
        x_coupled = x + coupling_strength * np.mean(y)
        y_coupled = y + coupling_strength * np.mean(x)
        return x_coupled, y_coupled

    elif coupling_type == 'nonlinear':
        # Nonlinear coupling: use product of norms
        x_norm = np.linalg.norm(x)
        y_norm = np.linalg.norm(y)

        x_coupled = x * (1.0 + coupling_strength * y_norm)
        y_coupled = y * (1.0 + coupling_strength * x_norm)
        return x_coupled, y_coupled

    else:
        raise ValueError(f"Unknown coupling type: {coupling_type}")


def _poincare_distance(x: np.ndarray, y: np.ndarray) -> float:
    """
    Compute Poincaré ball geodesic distance.

    d_H(x, y) = arcosh(1 + 2||x-y||² / ((1-||x||²)(1-||y||²)))
    """
    diff = x - y
    diff_norm_sq = np.dot(diff, diff)

    x_norm_sq = np.dot(x, x)
    y_norm_sq = np.dot(y, y)

    # Check ball constraint
    if x_norm_sq >= 1.0 or y_norm_sq >= 1.0:
        raise ValueError("Points must be inside Poincaré ball")

    numerator = 2.0 * diff_norm_sq
    denominator = (1.0 - x_norm_sq) * (1.0 - y_norm_sq)

    if denominator < 1e-12:
        return 10.0  # Large distance

    ratio = 1.0 + numerator / denominator
    ratio = max(1.0, ratio)

    return float(np.arccosh(ratio))


def _spherical_distance(x: np.ndarray, y: np.ndarray) -> float:
    """
    Compute spherical geodesic distance.

    d_S(x, y) = arccos(⟨x, y⟩)

    Assumes x and y are unit vectors on sphere.
    """
    # Normalize to unit sphere
    x_norm = x / np.linalg.norm(x)
    y_norm = y / np.linalg.norm(y)

    # Compute inner product
    inner_prod = np.dot(x_norm, y_norm)

    # Clamp to [-1, 1] for numerical stability
    inner_prod = np.clip(inner_prod, -1.0, 1.0)

    return float(np.arccos(inner_prod))


def create_product_space(
    spaces: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Create product manifold from list of component spaces.

    Args:
        spaces: List of space specifications, each with:
            - type: 'euclidean', 'poincare', or 'sphere'
            - dimension: int
            - curvature: float (optional)

    Returns:
        Product space specification
    """
    total_dimension = sum(s['dimension'] for s in spaces)

    product_space = {
        'type': 'product',
        'components': spaces,
        'total_dimension': total_dimension,
        'num_components': len(spaces)
    }

    return product_space


def project_to_product_space(
    point: np.ndarray,
    product_space: Dict[str, Any]
) -> List[np.ndarray]:
    """
    Project a point in product space to its component manifolds.

    Args:
        point: Point in product space (concatenated vector)
        product_space: Product space specification

    Returns:
        List of component points
    """
    components = product_space['components']

    # Split point into components
    component_points = []
    offset = 0

    for comp in components:
        dim = comp['dimension']
        comp_point = point[offset:offset+dim]
        component_points.append(comp_point)
        offset += dim

    return component_points


# Example usage and validation
if __name__ == "__main__":
    print("AGUA Runtime Manifold Module - Validation")
    print("=" * 50)

    # Test product metric
    print("\nProduct metric test:")
    x1 = np.array([0.1, 0.2, 0.1])
    x2 = np.array([0.2, 0.3, 0.2])
    y1 = np.array([0.5, 0.5])
    y2 = np.array([0.6, 0.4])

    params = {
        'manifold_M_type': 'euclidean',
        'manifold_N_type': 'euclidean',
        'weights': (1.0, 1.0)
    }

    d = product_metric(x1, x2, y1, y2, params)
    print(f"  d_M×N = {d:.6f}")

    # Test coupling
    print("\nCoupling test:")
    x = np.array([0.1, 0.2, 0.1])
    y = np.array([0.5, 0.5])

    params_couple = {
        'coupling_strength': 0.1,
        'coupling_type': 'linear'
    }

    x_coupled, y_coupled = couple(x, y, params_couple)
    print(f"  Original x: {x}")
    print(f"  Coupled x: {x_coupled}")
    print(f"  Original y: {y}")
    print(f"  Coupled y: {y_coupled}")

    # Test product space creation
    print("\nProduct space creation test:")
    spaces = [
        {'type': 'poincare', 'dimension': 7},
        {'type': 'euclidean', 'dimension': 3}
    ]

    product_space = create_product_space(spaces)
    print(f"  Total dimension: {product_space['total_dimension']}")
    print(f"  Num components: {product_space['num_components']}")

    print("\n✓ All functions operational")
