"""Spherical Geometry Operations

Provides 14 Core tier spherical geometry operations for positive curvature spaces (Sⁿ, κ > 0).
All operations are O(n) complexity with 1e-12 precision.

Based on unit sphere embedded in ℝⁿ⁺¹.
"""

import numpy as np
from typing import Union, Tuple

# Constants
EPSILON = 1e-12


def spherical_distance(x: np.ndarray, y: np.ndarray) -> float:
    """Compute geodesic distance on unit sphere using great circle arc.
    
    Formula: d(x,y) = arccos(⟨x,y⟩) for unit vectors
    
    Args:
        x: Point on Sⁿ (unit vector in ℝⁿ⁺¹)
        y: Point on Sⁿ (unit vector in ℝⁿ⁺¹)
    
    Returns:
        Geodesic distance in [0, π]
    
    Complexity: O(n)
    Precision: 1e-12
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    
    # Ensure unit vectors
    x = x / np.linalg.norm(x)
    y = y / np.linalg.norm(y)
    
    # Compute dot product
    dot = np.dot(x, y)
    
    # Clamp to [-1, 1] for numerical stability
    dot = np.clip(dot, -1.0, 1.0)
    
    distance = np.arccos(dot)
    
    return float(distance)


def spherical_exp_map(x: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Spherical exponential map from tangent space to sphere.
    
    Formula: exp_x(v) = cos(||v||)x + sin(||v||)(v/||v||)
    
    Args:
        x: Base point on Sⁿ (unit vector)
        v: Tangent vector in T_x Sⁿ (orthogonal to x)
    
    Returns:
        Point on Sⁿ
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    v = np.asarray(v, dtype=np.float64)
    
    # Ensure x is unit vector
    x = x / np.linalg.norm(x)
    
    norm_v = np.linalg.norm(v)
    
    if norm_v < EPSILON:
        return x
    
    # Project v to tangent space (ensure orthogonality)
    v = v - np.dot(v, x) * x
    norm_v = np.linalg.norm(v)
    
    if norm_v < EPSILON:
        return x
    
    # Exponential map formula
    result = np.cos(norm_v) * x + np.sin(norm_v) * (v / norm_v)
    
    # Ensure unit norm
    result = result / np.linalg.norm(result)
    
    return result


def spherical_log_map(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Spherical logarithmic map from sphere to tangent space.
    
    Formula: log_x(y) = (d(x,y)/sin(d(x,y)))(y - ⟨x,y⟩x)
    
    Args:
        x: Base point on Sⁿ
        y: Target point on Sⁿ (not antipodal to x)
    
    Returns:
        Tangent vector in T_x Sⁿ
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    
    # Ensure unit vectors
    x = x / np.linalg.norm(x)
    y = y / np.linalg.norm(y)
    
    dot = np.dot(x, y)
    dot = np.clip(dot, -1.0, 1.0)
    
    # Check for antipodal points
    if dot < -1.0 + EPSILON:
        raise ValueError("Points are antipodal, logarithmic map is not unique")
    
    # Compute distance
    distance = np.arccos(dot)
    
    if distance < EPSILON:
        return np.zeros_like(x)
    
    # Log map formula
    v = y - dot * x
    norm_v = np.linalg.norm(v)
    
    if norm_v < EPSILON:
        return np.zeros_like(x)
    
    result = (distance / np.sin(distance)) * v
    
    return result


def spherical_parallel_transport(x: np.ndarray, y: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Parallel transport tangent vector along geodesic.
    
    Formula: P_{x→y}(v) = v - (⟨v,x⟩/(1+⟨x,y⟩))(x+y)
    
    Args:
        x: Start point on Sⁿ
        y: End point on Sⁿ
        v: Tangent vector at x
    
    Returns:
        Tangent vector at y (parallel transported)
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    v = np.asarray(v, dtype=np.float64)
    
    # Ensure unit vectors
    x = x / np.linalg.norm(x)
    y = y / np.linalg.norm(y)
    
    # Ensure v is tangent
    v = v - np.dot(v, x) * x
    
    dot_xy = np.dot(x, y)
    
    # Parallel transport formula
    result = v - (np.dot(v, x) / (1 + dot_xy)) * (x + y)
    
    # Ensure tangency at y
    result = result - np.dot(result, y) * y
    
    return result


def spherical_geodesic(x: np.ndarray, v: np.ndarray, t: float) -> np.ndarray:
    """Compute point along great circle geodesic.
    
    Formula: γ(t) = cos(td)x + sin(td)(v/||v||), where d = ||v||
    
    Args:
        x: Start point on Sⁿ
        v: Tangent vector (direction and distance)
        t: Parameter in [0,1]
    
    Returns:
        Point on geodesic at parameter t
    
    Complexity: O(n)
    """
    return spherical_exp_map(x, t * v)


def spherical_projection(x: np.ndarray) -> np.ndarray:
    """Project point from ℝⁿ⁺¹ onto Sⁿ.
    
    Formula: proj(x) = x/||x||
    
    Args:
        x: Point in ℝⁿ⁺¹ (non-zero)
    
    Returns:
        Point on Sⁿ
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    norm = np.linalg.norm(x)
    
    if norm < EPSILON:
        raise ValueError("Cannot project zero vector onto sphere")
    
    return x / norm


def tangent_projection_spherical(x: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Project vector onto tangent space T_x Sⁿ.
    
    Formula: proj_{T_x}(v) = v - ⟨v,x⟩x
    
    Args:
        x: Point on Sⁿ
        v: Vector in ℝⁿ⁺¹
    
    Returns:
        Tangent vector in T_x Sⁿ
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    v = np.asarray(v, dtype=np.float64)
    
    # Ensure x is unit vector
    x = x / np.linalg.norm(x)
    
    # Project to tangent space
    result = v - np.dot(v, x) * x
    
    return result


def spherical_geodesic_midpoint(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Fast midpoint computation for two points.
    
    Formula: mid(x,y) = (x+y)/||x+y||
    
    Args:
        x: Point on Sⁿ
        y: Point on Sⁿ (not antipodal)
    
    Returns:
        Midpoint on geodesic
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    
    # Ensure unit vectors
    x = x / np.linalg.norm(x)
    y = y / np.linalg.norm(y)
    
    # Check for antipodal points
    dot = np.dot(x, y)
    if dot < -1.0 + EPSILON:
        raise ValueError("Points are antipodal, midpoint is not unique")
    
    # Midpoint formula
    midpoint = x + y
    result = midpoint / np.linalg.norm(midpoint)
    
    return result


def spherical_interpolation(x: np.ndarray, y: np.ndarray, t: float) -> np.ndarray:
    """Spherical linear interpolation (Slerp) along great circle.
    
    Formula: slerp(x,y,t) = sin((1-t)θ)/sin(θ)·x + sin(tθ)/sin(θ)·y
    
    Args:
        x: Start point on Sⁿ
        y: End point on Sⁿ
        t: Parameter in [0,1]
    
    Returns:
        Interpolated point on geodesic
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    
    # Ensure unit vectors
    x = x / np.linalg.norm(x)
    y = y / np.linalg.norm(y)
    
    dot = np.dot(x, y)
    dot = np.clip(dot, -1.0, 1.0)
    
    theta = np.arccos(dot)
    
    if theta < EPSILON:
        # Points are very close, use linear interpolation
        result = (1 - t) * x + t * y
        return result / np.linalg.norm(result)
    
    # Slerp formula
    sin_theta = np.sin(theta)
    coef_x = np.sin((1 - t) * theta) / sin_theta
    coef_y = np.sin(t * theta) / sin_theta
    
    result = coef_x * x + coef_y * y
    
    # Ensure unit norm
    result = result / np.linalg.norm(result)
    
    return result


def spherical_retraction(x: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Fast approximate exponential map for optimization.
    
    Formula: R_x(v) = (x+v)/||x+v||
    
    Args:
        x: Point on Sⁿ
        v: Tangent vector (small)
    
    Returns:
        Point on Sⁿ
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    v = np.asarray(v, dtype=np.float64)
    
    # Ensure x is unit vector
    x = x / np.linalg.norm(x)
    
    # Retraction formula
    result = x + v
    result = result / np.linalg.norm(result)
    
    return result


def stereographic_projection(x: np.ndarray) -> np.ndarray:
    """Project Sⁿ to ℝⁿ via stereographic projection.
    
    Formula: σ(x) = (x₁,...,xₙ)/(1-xₙ₊₁)
    
    Args:
        x: Point on Sⁿ (not south pole)
    
    Returns:
        Point in ℝⁿ
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    
    # Ensure unit vector
    x = x / np.linalg.norm(x)
    
    # Check if at south pole
    if x[-1] < -1.0 + EPSILON:
        raise ValueError("Cannot project from south pole")
    
    # Stereographic projection formula
    result = x[:-1] / (1 - x[-1])
    
    return result


def inverse_stereographic(y: np.ndarray) -> np.ndarray:
    """Lift point from ℝⁿ to Sⁿ via inverse stereographic projection.
    
    Formula: σ⁻¹(y) = (2y, ||y||²-1)/(1+||y||²)
    
    Args:
        y: Point in ℝⁿ
    
    Returns:
        Point on Sⁿ
    
    Complexity: O(n)
    """
    y = np.asarray(y, dtype=np.float64)
    
    norm_y_sq = np.sum(y ** 2)
    
    # Inverse stereographic formula
    denom = 1 + norm_y_sq
    space_coords = (2 / denom) * y
    last_coord = (norm_y_sq - 1) / denom
    
    result = np.concatenate([space_coords, [last_coord]])
    
    # Ensure unit norm
    result = result / np.linalg.norm(result)
    
    return result


def spherical_reflection(x: np.ndarray, hyperplane_normal: np.ndarray) -> np.ndarray:
    """Reflect point through great sphere (hyperplane).
    
    Formula: R_H(x) = x - 2⟨x,n⟩n for hyperplane normal n
    
    Args:
        x: Point on Sⁿ
        hyperplane_normal: Unit normal n
    
    Returns:
        Reflected point on Sⁿ
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    n = np.asarray(hyperplane_normal, dtype=np.float64)
    
    # Ensure unit vectors
    x = x / np.linalg.norm(x)
    n = n / np.linalg.norm(n)
    
    # Reflection formula
    dot = np.dot(x, n)
    result = x - 2 * dot * n
    
    # Ensure unit norm
    result = result / np.linalg.norm(result)
    
    return result


def spherical_to_hyperbolic(x_spherical: np.ndarray, target_kappa: float = -1.0) -> np.ndarray:
    """Convert between spherical (κ>0) and hyperbolic (κ<0) via analytic continuation.
    
    Maps through κ=0 (flat space) using stereographic projection and scaling.
    
    Args:
        x_spherical: Point on Sⁿ
        target_kappa: Target curvature κ < 0
    
    Returns:
        Corresponding point in hyperbolic space
    
    Complexity: O(n)
    """
    x = np.asarray(x_spherical, dtype=np.float64)
    
    # Ensure unit vector
    x = x / np.linalg.norm(x)
    
    # Convert via stereographic projection to flat space
    flat = stereographic_projection(x)
    
    # Scale by curvature ratio
    scale = np.sqrt(-target_kappa)
    scaled = flat * scale
    
    # Convert to hyperbolic (Poincaré ball)
    # Use tanh scaling to map to unit ball
    norm = np.linalg.norm(scaled)
    if norm > 0:
        hyperbolic = np.tanh(norm) * (scaled / norm)
    else:
        hyperbolic = scaled
    
    return hyperbolic
