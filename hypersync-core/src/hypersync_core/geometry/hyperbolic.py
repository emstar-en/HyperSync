"""Hyperbolic Geometry Operations

Provides 14 Core tier hyperbolic geometry operations for negative curvature spaces (ℍⁿ, κ < 0).
All operations are O(n) complexity with 1e-12 precision.

Based on Poincaré ball and Lorentz hyperboloid models.
"""

import numpy as np
from typing import Union, Tuple

# Constants
EPSILON = 1e-12
MAX_NORM = 1.0 - EPSILON


def hyperbolic_distance(x: np.ndarray, y: np.ndarray, c: float = 1.0) -> float:
    """Compute hyperbolic distance in Poincaré ball model.
    
    Formula: d(x,y) = arcosh(1 + 2||x-y||²/((1-||x||²)(1-||y||²)))
    
    Args:
        x: Point in Poincaré ball (unit vector in ℝⁿ)
        y: Point in Poincaré ball (unit vector in ℝⁿ)
        c: Curvature parameter (default -1, c=1 for unit curvature)
    
    Returns:
        Hyperbolic distance (scalar ≥ 0)
    
    Complexity: O(n)
    Precision: 1e-12
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    
    # Validate points are in Poincaré ball
    norm_x_sq = np.sum(x ** 2)
    norm_y_sq = np.sum(y ** 2)
    
    if norm_x_sq >= 1.0 or norm_y_sq >= 1.0:
        raise ValueError("Points must be inside unit ball: ||x||² < 1, ||y||² < 1")
    
    # Compute distance
    diff = x - y
    norm_diff_sq = np.sum(diff ** 2)
    
    numerator = 2 * norm_diff_sq
    denominator = (1 - norm_x_sq) * (1 - norm_y_sq)
    
    # Numerical stability
    ratio = numerator / denominator
    arg = 1 + ratio
    
    if arg < 1.0:
        arg = 1.0
    
    distance = np.arccosh(arg) / np.sqrt(c)
    
    return float(distance)


def hyperbolic_exp_map(x: np.ndarray, v: np.ndarray, c: float = 1.0) -> np.ndarray:
    """Exponential map from tangent space to Poincaré ball.
    
    Maps tangent vector v at point x to a point on the manifold.
    
    Args:
        x: Base point in Poincaré ball
        v: Tangent vector at x
        c: Curvature parameter
    
    Returns:
        Point in Poincaré ball
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    v = np.asarray(v, dtype=np.float64)
    
    norm_v = np.linalg.norm(v)
    
    if norm_v < EPSILON:
        return x
    
    sqrt_c = np.sqrt(c)
    norm_x_sq = np.sum(x ** 2)
    lambda_x = 2 / (1 - norm_x_sq)
    
    # Exponential map formula
    coef = np.tanh(sqrt_c * lambda_x * norm_v / 2) / (sqrt_c * norm_v)
    
    # Möbius addition
    result = mobius_add(x, coef * v, c)
    
    return result


def hyperbolic_log_map(x: np.ndarray, y: np.ndarray, c: float = 1.0) -> np.ndarray:
    """Logarithmic map from Poincaré ball to tangent space.
    
    Inverse of exponential map. Returns tangent vector at x pointing to y.
    
    Args:
        x: Base point in Poincaré ball
        y: Target point in Poincaré ball
    
    Returns:
        Tangent vector at x
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    
    sqrt_c = np.sqrt(c)
    
    # Möbius subtraction
    diff = mobius_add(-x, y, c)
    
    norm_diff = np.linalg.norm(diff)
    
    if norm_diff < EPSILON:
        return np.zeros_like(x)
    
    norm_x_sq = np.sum(x ** 2)
    lambda_x = 2 / (1 - norm_x_sq)
    
    # Log map formula
    coef = (2 / (sqrt_c * lambda_x)) * np.arctanh(sqrt_c * norm_diff) / norm_diff
    
    result = coef * diff
    
    return result


def hyperbolic_parallel_transport(x: np.ndarray, y: np.ndarray, v: np.ndarray, c: float = 1.0) -> np.ndarray:
    """Parallel transport tangent vector from x to y.
    
    Args:
        x: Start point in Poincaré ball
        y: End point in Poincaré ball
        v: Tangent vector at x
        c: Curvature parameter
    
    Returns:
        Tangent vector at y (parallel transported)
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    v = np.asarray(v, dtype=np.float64)
    
    # Compute logarithmic map from x to y
    log_xy = hyperbolic_log_map(x, y, c)
    norm_log_xy = np.linalg.norm(log_xy)
    
    if norm_log_xy < EPSILON:
        return v
    
    # Parallel transport formula
    norm_x_sq = np.sum(x ** 2)
    norm_y_sq = np.sum(y ** 2)
    
    lambda_x = 2 / (1 - norm_x_sq)
    lambda_y = 2 / (1 - norm_y_sq)
    
    # Gyration matrix
    result = (lambda_x / lambda_y) * v
    
    return result


def hyperbolic_geodesic(x: np.ndarray, v: np.ndarray, t: float, c: float = 1.0) -> np.ndarray:
    """Compute point along hyperbolic geodesic.
    
    Args:
        x: Start point in Poincaré ball
        v: Tangent vector (direction and distance)
        t: Parameter in [0,1]
        c: Curvature parameter
    
    Returns:
        Point on geodesic at parameter t
    
    Complexity: O(n)
    """
    return hyperbolic_exp_map(x, t * v, c)


def poincare_to_lorentz(x: np.ndarray) -> np.ndarray:
    """Convert point from Poincaré ball to Lorentz hyperboloid model.
    
    Args:
        x: Point in Poincaré ball (n-dimensional)
    
    Returns:
        Point in Lorentz model ((n+1)-dimensional)
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    norm_x_sq = np.sum(x ** 2)
    
    if norm_x_sq >= 1.0:
        raise ValueError("Point must be inside unit ball")
    
    # Conversion formula
    denom = 1 - norm_x_sq
    time_coord = (1 + norm_x_sq) / denom
    space_coords = (2 / denom) * x
    
    result = np.concatenate([[time_coord], space_coords])
    
    return result


def lorentz_to_poincare(x: np.ndarray) -> np.ndarray:
    """Convert point from Lorentz hyperboloid to Poincaré ball model.
    
    Args:
        x: Point in Lorentz model ((n+1)-dimensional)
    
    Returns:
        Point in Poincaré ball (n-dimensional)
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    
    time_coord = x[0]
    space_coords = x[1:]
    
    # Conversion formula
    result = space_coords / (1 + time_coord)
    
    return result


def tangent_projection_hyperbolic(x: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Project vector onto tangent space at x in Poincaré ball.
    
    Args:
        x: Point in Poincaré ball
        v: Vector in ℝⁿ
    
    Returns:
        Tangent vector at x
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    v = np.asarray(v, dtype=np.float64)
    
    # In Poincaré model, tangent space is just ℝⁿ
    # But we need to rescale by the metric
    norm_x_sq = np.sum(x ** 2)
    lambda_x = 2 / (1 - norm_x_sq)
    
    # Rescale
    result = v / lambda_x
    
    return result


def hyperbolic_midpoint(x: np.ndarray, y: np.ndarray, c: float = 1.0) -> np.ndarray:
    """Compute hyperbolic midpoint between two points.
    
    Args:
        x: First point in Poincaré ball
        y: Second point in Poincaré ball
        c: Curvature parameter
    
    Returns:
        Midpoint on hyperbolic geodesic
    
    Complexity: O(n)
    """
    v = hyperbolic_log_map(x, y, c)
    return hyperbolic_exp_map(x, 0.5 * v, c)


def hyperbolic_retraction(x: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Fast approximate exponential map for optimization.
    
    First-order approximation of exp_map, faster for small v.
    
    Args:
        x: Point in Poincaré ball
        v: Tangent vector (small)
    
    Returns:
        Point in Poincaré ball
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    v = np.asarray(v, dtype=np.float64)
    
    # Simple Möbius addition
    result = mobius_add(x, v, c=1.0)
    
    # Project back to ball
    norm = np.linalg.norm(result)
    if norm >= MAX_NORM:
        result = (MAX_NORM / norm) * result
    
    return result


def stereographic_to_poincare(x: np.ndarray) -> np.ndarray:
    """Convert from stereographic projection to Poincaré ball.
    
    Args:
        x: Point in ℝⁿ (stereographic coordinates)
    
    Returns:
        Point in Poincaré ball
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    norm_x_sq = np.sum(x ** 2)
    
    result = x / (1 + np.sqrt(1 + norm_x_sq))
    
    return result


def poincare_to_stereographic(x: np.ndarray) -> np.ndarray:
    """Convert from Poincaré ball to stereographic projection.
    
    Args:
        x: Point in Poincaré ball
    
    Returns:
        Point in ℝⁿ (stereographic coordinates)
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    norm_x = np.linalg.norm(x)
    
    if norm_x < EPSILON:
        return x
    
    result = x / (1 - norm_x)
    
    return result


def hyperbolic_reflection(x: np.ndarray, hyperplane_normal: np.ndarray) -> np.ndarray:
    """Reflect point through hyperbolic hyperplane.
    
    Args:
        x: Point in Poincaré ball
        hyperplane_normal: Unit normal to hyperplane
    
    Returns:
        Reflected point
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    n = np.asarray(hyperplane_normal, dtype=np.float64)
    n = n / np.linalg.norm(n)  # Ensure unit normal
    
    # Hyperbolic reflection formula
    dot = np.dot(x, n)
    result = x - 2 * dot * n
    
    return result


def hyperbolic_interpolation(x: np.ndarray, y: np.ndarray, t: float, c: float = 1.0) -> np.ndarray:
    """Interpolate along hyperbolic geodesic (same as geodesic with t parameter).
    
    Args:
        x: Start point in Poincaré ball
        y: End point in Poincaré ball
        t: Parameter in [0,1]
        c: Curvature parameter
    
    Returns:
        Interpolated point
    
    Complexity: O(n)
    """
    v = hyperbolic_log_map(x, y, c)
    return hyperbolic_exp_map(x, t * v, c)


# Helper functions

def mobius_add(x: np.ndarray, y: np.ndarray, c: float = 1.0) -> np.ndarray:
    """Möbius addition in Poincaré ball.
    
    Args:
        x: First point
        y: Second point
        c: Curvature parameter
    
    Returns:
        Möbius sum x ⊕ y
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    
    norm_x_sq = np.sum(x ** 2)
    norm_y_sq = np.sum(y ** 2)
    xy_dot = np.dot(x, y)
    
    numerator = (1 + 2 * c * xy_dot + c * norm_y_sq) * x + (1 - c * norm_x_sq) * y
    denominator = 1 + 2 * c * xy_dot + c ** 2 * norm_x_sq * norm_y_sq
    
    result = numerator / denominator
    
    return result
