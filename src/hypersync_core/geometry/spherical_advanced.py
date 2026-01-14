"""Advanced Spherical Geometry Operations

Additional spherical geometry utilities including:
- Barycenter computation (Riemannian center of mass)
- Curvature calculation
- Volume and area computation on sphere
- Visualization helpers
"""

import numpy as np
from typing import List, Tuple
from .spherical import (
    spherical_distance,
    spherical_exp_map,
    spherical_log_map,
    spherical_projection,
    spherical_geodesic_midpoint,
    EPSILON,
)


def spherical_mean(points: List[np.ndarray], max_iter: int = 100) -> np.ndarray:
    """Compute spherical Fréchet mean (Riemannian center of mass).
    
    The Fréchet mean on the sphere minimizes:
    
    $$\\bar{x} = \\arg\\min_{x \\in S^n} \\sum_{i=1}^N d_S(x, x_i)^2$$
    
    where $d_S$ is the spherical geodesic distance.
    
    Uses intrinsic gradient descent on the manifold.
    
    Args:
        points: List of points on unit sphere
        max_iter: Maximum gradient descent iterations
    
    Returns:
        Fréchet mean on sphere
    
    Complexity: O(n × m × k)
    Precision: 1e-8
    
    Algorithm:
    1. Initialize at first point
    2. Compute gradient = average of log maps
    3. Update: $x_{t+1} = \\exp_x(-\\eta \\nabla f)$
    4. Repeat until convergence
    """
    if len(points) == 0:
        raise ValueError("Cannot compute mean of empty set")
    
    if len(points) == 1:
        return points[0].copy()
    
    # Initialize at first point
    mean = points[0].copy()
    mean = spherical_projection(mean)
    step_size = 0.5
    
    for iteration in range(max_iter):
        # Compute Riemannian gradient
        gradient = np.zeros_like(mean)
        
        for point in points:
            try:
                log_map = spherical_log_map(mean, point)
                gradient += log_map
            except ValueError:
                # Skip antipodal points
                continue
        
        gradient = gradient / len(points)
        
        # Check convergence
        grad_norm = np.linalg.norm(gradient)
        if grad_norm < EPSILON:
            break
        
        # Update via exponential map
        mean = spherical_exp_map(mean, -step_size * gradient)
        
        # Ensure on sphere
        mean = spherical_projection(mean)
        
        # Adaptive step size
        if iteration > 20 and grad_norm > 0.1:
            step_size *= 0.95
    
    return mean


def spherical_variance(points: List[np.ndarray], mean: np.ndarray = None) -> float:
    """Compute spherical variance.
    
    Variance is the average squared geodesic distance to mean:
    
    $$\\text{Var}(X) = \\frac{1}{N} \\sum_{i=1}^N d_S(\\bar{x}, x_i)^2$$
    
    Args:
        points: List of points on sphere
        mean: Precomputed mean (optional)
    
    Returns:
        Variance (scalar ≥ 0)
    
    Complexity: O(n × m)
    """
    if len(points) == 0:
        return 0.0
    
    if mean is None:
        mean = spherical_mean(points)
    
    variance = 0.0
    for point in points:
        dist = spherical_distance(mean, point)
        variance += dist ** 2
    
    variance /= len(points)
    
    return float(variance)


def spherical_sectional_curvature(x: np.ndarray, radius: float = 1.0) -> float:
    """Compute sectional curvature of sphere.
    
    For a sphere of radius $R$, the sectional curvature is:
    $$K = \\frac{1}{R^2}$$
    
    For unit sphere: $K = 1$
    
    Args:
        x: Point on sphere (unused, curvature is constant)
        radius: Radius of sphere
    
    Returns:
        Sectional curvature (constant 1/R²)
    
    Complexity: O(1)
    """
    return 1.0 / (radius ** 2)


def spherical_volume_element(x: np.ndarray) -> float:
    """Compute volume element at point x on sphere.
    
    For unit sphere $S^n$, the volume element is simply:
    $$dV = dS$$
    
    (The Riemannian metric is the induced metric from $\\mathbb{R}^{n+1}$)
    
    Args:
        x: Point on sphere
    
    Returns:
        Volume element (1.0 for unit sphere)
    
    Complexity: O(1)
    """
    return 1.0


def spherical_cap_volume(radius: float, dimension: int, height: float) -> float:
    """Compute volume of spherical cap.
    
    A spherical cap is the region of a sphere cut off by a hyperplane.
    
    For unit sphere $S^n$ and cap height $h$:
    $$V_{\\text{cap}}(h) = \\frac{\\pi^{n/2}}{\\Gamma(n/2+1)} \\int_0^{\\arccos(1-h)} \\sin^n(\\theta) d\\theta$$
    
    Simplified for $S^2$ (3D sphere):
    $$V = \\pi h^2(3R - h)/3$$
    
    Args:
        radius: Radius of sphere
        dimension: Dimension of sphere (n for S^n)
        height: Height of cap
    
    Returns:
        Volume of spherical cap
    
    Complexity: O(1) for n=2; O(n) otherwise
    """
    if height <= 0:
        return 0.0
    
    if height > 2 * radius:
        # Full sphere
        return spherical_surface_area(radius, dimension)
    
    if dimension == 2:
        # Closed form for S^2 (surface area)
        area = 2 * np.pi * radius * height
    elif dimension == 3:
        # Volume formula for 3D cap
        volume = np.pi * height ** 2 * (3 * radius - height) / 3
        return volume
    else:
        # Numerical integration for higher dimensions
        from scipy import integrate
        
        theta_max = np.arccos(1 - height / radius) if height <= 2 * radius else np.pi
        
        def integrand(theta):
            return np.sin(theta) ** dimension
        
        integral, _ = integrate.quad(integrand, 0, theta_max)
        volume = (np.pi ** (dimension / 2) / np.math.gamma(dimension / 2 + 1)) * integral * (radius ** dimension)
    
    return float(volume)


def spherical_surface_area(radius: float, dimension: int) -> float:
    """Compute surface area (volume) of sphere.
    
    For unit sphere $S^n$ embedded in $\\mathbb{R}^{n+1}$:
    $$A(S^n) = \\frac{2\\pi^{(n+1)/2}}{\\Gamma((n+1)/2)}$$
    
    Common cases:
    - $S^1$: $A = 2\\pi R$ (circle circumference)
    - $S^2$: $A = 4\\pi R^2$ (sphere surface area)
    - $S^3$: $A = 2\\pi^2 R^3$ (3-sphere volume)
    
    Args:
        radius: Radius of sphere
        dimension: Dimension n (for S^n)
    
    Returns:
        Surface area/volume
    
    Complexity: O(1)
    """
    from scipy.special import gamma
    
    n = dimension
    
    area = (2 * np.pi ** ((n + 1) / 2) / gamma((n + 1) / 2)) * (radius ** n)
    
    return float(area)


def spherical_triangle_area(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """Compute area of spherical triangle on unit sphere.
    
    Uses spherical excess formula (Girard's theorem):
    $$A = \\alpha + \\beta + \\gamma - \\pi$$
    
    where $\\alpha, \\beta, \\gamma$ are interior angles.
    
    For radius $R$: $A = R^2(\\alpha + \\beta + \\gamma - \\pi)$
    
    Args:
        a, b, c: Vertices on unit sphere
    
    Returns:
        Area of spherical triangle
    
    Complexity: O(n)
    """
    # Ensure unit vectors
    a = spherical_projection(a)
    b = spherical_projection(b)
    c = spherical_projection(c)
    
    # Compute side lengths (great circle distances)
    side_a = spherical_distance(b, c)
    side_b = spherical_distance(c, a)
    side_c = spherical_distance(a, b)
    
    # Use spherical law of cosines to find angles
    # cos(α) = (cos(a) - cos(b)cos(c)) / (sin(b)sin(c))
    
    cos_alpha = (np.cos(side_a) - np.cos(side_b) * np.cos(side_c)) / \
                (np.sin(side_b) * np.sin(side_c) + EPSILON)
    cos_beta = (np.cos(side_b) - np.cos(side_c) * np.cos(side_a)) / \
               (np.sin(side_c) * np.sin(side_a) + EPSILON)
    cos_gamma = (np.cos(side_c) - np.cos(side_a) * np.cos(side_b)) / \
                (np.sin(side_a) * np.sin(side_b) + EPSILON)
    
    # Clamp for numerical stability
    cos_alpha = np.clip(cos_alpha, -1.0, 1.0)
    cos_beta = np.clip(cos_beta, -1.0, 1.0)
    cos_gamma = np.clip(cos_gamma, -1.0, 1.0)
    
    alpha = np.arccos(cos_alpha)
    beta = np.arccos(cos_beta)
    gamma = np.arccos(cos_gamma)
    
    # Spherical excess
    area = alpha + beta + gamma - np.pi
    
    return float(max(0.0, area))


def spherical_polygon_area(points: List[np.ndarray]) -> float:
    """Compute area of spherical polygon on unit sphere.
    
    Uses triangulation from first vertex.
    
    Args:
        points: Vertices on unit sphere (at least 3)
    
    Returns:
        Area of polygon
    
    Complexity: O(k) where k = number of vertices
    """
    k = len(points)
    
    if k < 3:
        return 0.0
    
    total_area = 0.0
    
    for i in range(1, k - 1):
        area = spherical_triangle_area(points[0], points[i], points[i + 1])
        total_area += area
    
    return total_area


def visualize_spherical_points_3d(points: List[np.ndarray], title: str = "Spherical Points"):
    """Visualize points on unit sphere in 3D.
    
    Args:
        points: List of 3D points on unit sphere
        title: Plot title
    
    Requires: matplotlib with 3D support
    """
    try:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
    except ImportError:
        print("Matplotlib with 3D support not installed. Install with: pip install matplotlib")
        return
    
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Draw unit sphere wireframe
    u = np.linspace(0, 2 * np.pi, 30)
    v = np.linspace(0, np.pi, 20)
    x_sphere = np.outer(np.cos(u), np.sin(v))
    y_sphere = np.outer(np.sin(u), np.sin(v))
    z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_wireframe(x_sphere, y_sphere, z_sphere, color='lightgray', alpha=0.3, linewidth=0.5)
    
    # Plot points
    points_array = np.array([p[:3] for p in points])  # Take first 3 dimensions
    ax.scatter(points_array[:, 0], points_array[:, 1], points_array[:, 2], 
               c='blue', s=100, depthshade=True, zorder=10)
    
    # Plot origin
    ax.scatter([0], [0], [0], c='red', s=150, marker='x', label='Origin', zorder=10)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title)
    ax.legend()
    
    # Equal aspect ratio
    max_range = 1.2
    ax.set_xlim([-max_range, max_range])
    ax.set_ylim([-max_range, max_range])
    ax.set_zlim([-max_range, max_range])
    
    plt.tight_layout()
    plt.show()
