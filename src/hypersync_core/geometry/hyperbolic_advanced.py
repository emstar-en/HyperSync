"""Advanced Hyperbolic Geometry Operations

Additional hyperbolic geometry utilities including:
- Barycenter computation
- Curvature calculation
- Volume and area computation
- Visualization helpers
"""

import numpy as np
from typing import List, Tuple
from .hyperbolic import (
    hyperbolic_distance,
    hyperbolic_exp_map,
    hyperbolic_log_map,
    hyperbolic_midpoint,
    EPSILON,
)


def hyperbolic_mean(points: List[np.ndarray], c: float = 1.0, max_iter: int = 100) -> np.ndarray:
    """Compute hyperbolic Fréchet mean (barycenter) in Poincaré ball.
    
    The Fréchet mean minimizes the sum of squared hyperbolic distances:
    
    $$\\bar{x} = \\arg\\min_{x \\in \\mathbb{H}^n} \\sum_{i=1}^N d_\\mathbb{H}(x, x_i)^2$$
    
    Uses gradient descent on the manifold.
    
    Args:
        points: List of points in Poincaré ball
        c: Curvature parameter
        max_iter: Maximum iterations for gradient descent
    
    Returns:
        Fréchet mean point
    
    Complexity: O(n × m × k) where n=num_points, m=dimension, k=iterations
    Precision: 1e-8
    
    Mathematical Details:
    The gradient descent update is:
    $$x_{t+1} = \\exp_x(-\\eta \\nabla f(x))$$
    where $f(x) = \\sum d_\\mathbb{H}(x, x_i)^2$
    """
    if len(points) == 0:
        raise ValueError("Cannot compute mean of empty set")
    
    if len(points) == 1:
        return points[0].copy()
    
    # Initialize at first point
    mean = points[0].copy()
    step_size = 0.1
    
    for iteration in range(max_iter):
        # Compute gradient: sum of log maps
        gradient = np.zeros_like(mean)
        
        for point in points:
            log_map = hyperbolic_log_map(mean, point, c)
            gradient += log_map
        
        gradient = gradient / len(points)
        
        # Check convergence
        grad_norm = np.linalg.norm(gradient)
        if grad_norm < EPSILON:
            break
        
        # Update via exponential map
        mean = hyperbolic_exp_map(mean, -step_size * gradient, c)
        
        # Adaptive step size
        if iteration > 10 and grad_norm > 1.0:
            step_size *= 0.9
    
    return mean


def hyperbolic_variance(points: List[np.ndarray], mean: np.ndarray = None, c: float = 1.0) -> float:
    """Compute hyperbolic variance.
    
    Variance is the average squared geodesic distance to the mean:
    
    $$\\text{Var}(X) = \\frac{1}{N} \\sum_{i=1}^N d_\\mathbb{H}(\\bar{x}, x_i)^2$$
    
    Args:
        points: List of points in Poincaré ball
        mean: Precomputed mean (optional, computed if None)
        c: Curvature parameter
    
    Returns:
        Variance (scalar ≥ 0)
    
    Complexity: O(n × m)
    """
    if len(points) == 0:
        return 0.0
    
    if mean is None:
        mean = hyperbolic_mean(points, c)
    
    variance = 0.0
    for point in points:
        dist = hyperbolic_distance(mean, point, c)
        variance += dist ** 2
    
    variance /= len(points)
    
    return float(variance)


def hyperbolic_sectional_curvature(x: np.ndarray, c: float = 1.0) -> float:
    """Compute sectional curvature at point x in Poincaré ball.
    
    For the Poincaré ball model with curvature parameter c:
    $$K = -c$$
    
    The sectional curvature is constant everywhere.
    
    Args:
        x: Point in Poincaré ball
        c: Curvature parameter
    
    Returns:
        Sectional curvature (constant -c)
    
    Complexity: O(1)
    """
    return -c


def hyperbolic_volume_element(x: np.ndarray, c: float = 1.0) -> float:
    """Compute volume element at point x.
    
    The volume element in the Poincaré ball is:
    
    $$dV = \\left(\\frac{2}{1 - c\\|x\\|^2}\\right)^n dx$$
    
    Args:
        x: Point in Poincaré ball
        c: Curvature parameter
    
    Returns:
        Volume element scaling factor
    
    Complexity: O(n)
    """
    x = np.asarray(x, dtype=np.float64)
    norm_sq = np.sum(x ** 2)
    
    n = len(x)
    lambda_x = 2 / (1 - c * norm_sq)
    
    volume_element = lambda_x ** n
    
    return float(volume_element)


def hyperbolic_ball_volume(radius: float, dimension: int, c: float = 1.0) -> float:
    """Compute volume of hyperbolic ball of given radius.
    
    For a ball of radius $r$ in $\\mathbb{H}^n$ with curvature $-c$:
    
    $$V_n(r) = \\frac{\\pi^{n/2}}{\\Gamma(n/2+1)} \\int_0^r \\sinh^{n-1}(\\sqrt{c}t) dt$$
    
    For $n=2$: $V_2(r) = 2\\pi(\\cosh(\\sqrt{c}r) - 1)/c$
    
    Args:
        radius: Radius of ball
        dimension: Dimension of hyperbolic space
        c: Curvature parameter
    
    Returns:
        Volume of ball
    
    Complexity: O(1) for n=2,3; O(n) otherwise
    """
    if radius <= 0:
        return 0.0
    
    sqrt_c = np.sqrt(c)
    
    if dimension == 2:
        # Closed form for H^2
        volume = 2 * np.pi * (np.cosh(sqrt_c * radius) - 1) / c
    elif dimension == 3:
        # Closed form for H^3  
        volume = 2 * np.pi * (np.sinh(sqrt_c * radius) / sqrt_c - radius) / c
    else:
        # Numerical integration for higher dimensions
        from scipy import integrate
        
        def integrand(t):
            return np.sinh(sqrt_c * t) ** (dimension - 1)
        
        integral, _ = integrate.quad(integrand, 0, radius)
        volume = (np.pi ** (dimension / 2) / np.math.gamma(dimension / 2 + 1)) * integral
    
    return float(volume)


def hyperbolic_geodesic_area(points: List[np.ndarray], c: float = 1.0) -> float:
    """Compute area of hyperbolic polygon (for n=2).
    
    Uses Gauss-Bonnet theorem:
    $$A = (k-2)\\pi - \\sum_{i=1}^k \\theta_i + \\int_P K dA$$
    
    For hyperbolic plane: $K = -c$, so:
    $$A = -\\frac{1}{c}[(k-2)\\pi - \\sum \\theta_i]$$
    
    Simplified approximation: use triangulation.
    
    Args:
        points: Vertices of polygon (at least 3 points)
        c: Curvature parameter
    
    Returns:
        Area of hyperbolic polygon
    
    Complexity: O(k) where k = number of vertices
    """
    k = len(points)
    
    if k < 3:
        return 0.0
    
    # Simplified: compute area of star-shaped polygon from first vertex
    total_area = 0.0
    
    for i in range(1, k - 1):
        # Triangle: points[0], points[i], points[i+1]
        area = hyperbolic_triangle_area(points[0], points[i], points[i + 1], c)
        total_area += area
    
    return total_area


def hyperbolic_triangle_area(a: np.ndarray, b: np.ndarray, c_point: np.ndarray, c: float = 1.0) -> float:
    """Compute area of hyperbolic triangle.
    
    Uses formula:
    $$A = \\pi - (\\alpha + \\beta + \\gamma)$$
    where $\\alpha, \\beta, \\gamma$ are interior angles.
    
    For curvature $-c$:
    $$A = \\frac{1}{c}[\\pi - (\\alpha + \\beta + \\gamma)]$$
    
    Args:
        a, b, c_point: Vertices of triangle
        c: Curvature parameter
    
    Returns:
        Area of triangle
    
    Complexity: O(n)
    """
    # Compute side lengths
    side_a = hyperbolic_distance(b, c_point, c)
    side_b = hyperbolic_distance(c_point, a, c)
    side_c = hyperbolic_distance(a, b, c)
    
    # Use hyperbolic law of cosines to get angles
    # cos(α) = (cosh(b)cosh(c) - cosh(a)) / (sinh(b)sinh(c))
    sqrt_c = np.sqrt(c)
    
    # Scale by sqrt(c) for proper curvature
    a_scaled = sqrt_c * side_a
    b_scaled = sqrt_c * side_b
    c_scaled = sqrt_c * side_c
    
    # Compute angles using law of cosines
    cos_alpha = (np.cosh(b_scaled) * np.cosh(c_scaled) - np.cosh(a_scaled)) / \
                (np.sinh(b_scaled) * np.sinh(c_scaled) + EPSILON)
    cos_beta = (np.cosh(c_scaled) * np.cosh(a_scaled) - np.cosh(b_scaled)) / \
               (np.sinh(c_scaled) * np.sinh(a_scaled) + EPSILON)
    cos_gamma = (np.cosh(a_scaled) * np.cosh(b_scaled) - np.cosh(c_scaled)) / \
                (np.sinh(a_scaled) * np.sinh(b_scaled) + EPSILON)
    
    # Clamp for numerical stability
    cos_alpha = np.clip(cos_alpha, -1.0, 1.0)
    cos_beta = np.clip(cos_beta, -1.0, 1.0)
    cos_gamma = np.clip(cos_gamma, -1.0, 1.0)
    
    alpha = np.arccos(cos_alpha)
    beta = np.arccos(cos_beta)
    gamma = np.arccos(cos_gamma)
    
    # Area from angle deficit
    area = (np.pi - (alpha + beta + gamma)) / c
    
    return float(max(0.0, area))


def visualize_hyperbolic_points_2d(points: List[np.ndarray], title: str = "Hyperbolic Points"):
    """Visualize points in Poincaré disk (for 2D hyperbolic space).
    
    Args:
        points: List of 2D points in Poincaré disk
        title: Plot title
    
    Requires: matplotlib
    """
    try:
        import matplotlib.pyplot as plt
        from matplotlib.patches import Circle
    except ImportError:
        print("Matplotlib not installed. Install with: pip install matplotlib")
        return
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Draw unit disk boundary
    circle = Circle((0, 0), 1.0, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(circle)
    
    # Plot points
    points_array = np.array([p[:2] for p in points])  # Take first 2 dimensions
    ax.scatter(points_array[:, 0], points_array[:, 1], c='blue', s=50, zorder=3)
    
    # Plot origin
    ax.scatter([0], [0], c='red', s=100, marker='x', label='Origin', zorder=3)
    
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_title(title)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    
    plt.tight_layout()
    plt.show()
