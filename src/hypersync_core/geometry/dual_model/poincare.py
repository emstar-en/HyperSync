"""
Poincaré Ball Model for Hyperbolic Geometry

This module implements the Poincaré ball model for hyperbolic geometry.
Points lie in the open unit ball in ℝ^n:

    B^n = {x ∈ ℝ^n : ||x|| < 1}

with Riemannian metric:
    ds² = 4/(1-||x||²)² * ||dx||²

Mathematical Background:
- The Poincaré ball model is conformal (preserves angles)
- Geodesics are either diameters or circular arcs perpendicular to the boundary
- The boundary represents points at infinity
- Distance formula involves the cross-ratio

References:
- Anderson "Hyperbolic Geometry" (2005)
- Cannon et al. "Hyperbolic Geometry" (1997)
"""

import numpy as np
from typing import Optional, Union, List, Tuple
import warnings


class PoincareModel:
    """
    Poincaré ball model for hyperbolic geometry.
    
    This class provides implementations of hyperbolic geometric operations
    using the Poincaré ball model. This model is particularly intuitive
    and well-suited for visualization.
    
    Attributes:
        dim (int): Dimension of the hyperbolic space (n in B^n)
        eps (float): Numerical stability epsilon
    """
    
    def __init__(self, dim: int = 2, eps: float = 1e-12):
        """
        Initialize Poincaré ball model.
        
        Args:
            dim: Dimension of hyperbolic space (must be >= 1)
            eps: Numerical precision for stability checks
            
        Raises:
            ValueError: If dimension is less than 1
        """
        if dim < 1:
            raise ValueError(f"Dimension must be >= 1, got {dim}")
        self.dim = dim
        self.eps = eps
        
    def _lambda(self, x: np.ndarray) -> Union[float, np.ndarray]:
        """
        Compute conformal factor λ(x) = 2/(1-||x||²).
        
        This factor appears in the Poincaré metric and many formulas.
        
        Args:
            x: Point in Poincaré ball, shape (..., dim)
            
        Returns:
            Conformal factor(s)
        """
        x = np.asarray(x, dtype=np.float64)
        norm_sq = np.sum(x**2, axis=-1)
        return 2.0 / (1.0 - norm_sq + self.eps)
    
    def poincare_inner_product(self, x: np.ndarray, u: np.ndarray, v: np.ndarray) -> Union[float, np.ndarray]:
        """
        Compute Riemannian inner product in tangent space at x.
        
        Mathematical formula:
            <u,v>_x = (λ(x)/2)² * <u,v>_euclidean
        
        where λ(x) = 2/(1-||x||²) is the conformal factor.
        
        Args:
            x: Base point in Poincaré ball, shape (..., dim)
            u: Tangent vector at x, shape (..., dim)
            v: Tangent vector at x, shape (..., dim)
            
        Returns:
            Riemannian inner product value(s)
            
        Example:
            >>> model = PoincareModel(dim=2)
            >>> x = np.array([0.0, 0.0])  # Origin
            >>> u = np.array([1.0, 0.0])
            >>> v = np.array([0.0, 1.0])
            >>> model.poincare_inner_product(x, u, v)
            0.0
        """
        x = np.asarray(x, dtype=np.float64)
        u = np.asarray(u, dtype=np.float64)
        v = np.asarray(v, dtype=np.float64)
        
        # Validate x is in ball
        self._validate_in_ball(x)
        
        # Compute conformal factor
        lambda_x = self._lambda(x)
        
        # Riemannian metric
        euclidean_inner = np.sum(u * v, axis=-1)
        return (lambda_x / 2.0) ** 2 * euclidean_inner
    
    def poincare_norm(self, x: np.ndarray, v: np.ndarray) -> Union[float, np.ndarray]:
        """
        Compute norm of tangent vector in Riemannian metric.
        
        Mathematical formula:
            ||v||_x = (λ(x)/2) * ||v||_euclidean
        
        Args:
            x: Base point in Poincaré ball, shape (..., dim)
            v: Tangent vector at x, shape (..., dim)
            
        Returns:
            Riemannian norm(s)
        """
        return np.sqrt(self.poincare_inner_product(x, v, v))
    
    def poincare_distance(self, x: np.ndarray, y: np.ndarray) -> Union[float, np.ndarray]:
        """
        Compute geodesic distance in Poincaré ball.
        
        Mathematical formula:
            d(x,y) = arcosh(1 + 2*||x-y||²/((1-||x||²)(1-||y||²)))
        
        Alternatively using cross-ratio:
            d(x,y) = 2*arctanh(||(-x)⊕y||)
        
        where ⊕ is the Möbius addition.
        
        Properties:
            - Always non-negative
            - Symmetric: d(x,y) = d(y,x)
            - Triangle inequality
            - d(x,y) = 0 iff x = y
        
        Args:
            x: Point in Poincaré ball, shape (..., dim)
            y: Point in Poincaré ball, shape (..., dim)
            
        Returns:
            Hyperbolic distance(s)
            
        Example:
            >>> model = PoincareModel(dim=2)
            >>> x = np.array([0.0, 0.0])
            >>> y = np.array([0.5, 0.0])
            >>> dist = model.poincare_distance(x, y)
        """
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        
        # Validate points are in ball
        self._validate_in_ball(x)
        self._validate_in_ball(y)
        
        # Compute norms
        x_norm_sq = np.sum(x**2, axis=-1)
        y_norm_sq = np.sum(y**2, axis=-1)
        xy_diff_norm_sq = np.sum((x - y)**2, axis=-1)
        
        # Distance formula
        numerator = 2.0 * xy_diff_norm_sq
        denominator = (1.0 - x_norm_sq) * (1.0 - y_norm_sq) + self.eps
        
        arg = 1.0 + numerator / denominator
        arg = np.maximum(arg, 1.0 + self.eps)  # Numerical stability
        
        return np.arccosh(arg)
    
    def poincare_projection(self, x: np.ndarray) -> np.ndarray:
        """
        Project point onto Poincaré ball surface (if outside).
        
        Clips points to be within the ball with small margin from boundary.
        
        Args:
            x: Point in ℝ^n, shape (..., dim)
            
        Returns:
            Projected point in Poincaré ball
        """
        x = np.asarray(x, dtype=np.float64)
        norm = np.linalg.norm(x, axis=-1, keepdims=True)
        
        # If outside ball, project to boundary with margin
        max_norm = 1.0 - self.eps
        scale = np.where(norm > max_norm, max_norm / (norm + self.eps), 1.0)
        
        return x * scale
    
    def mobius_addition(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        Compute Möbius addition x ⊕ y.
        
        Mathematical formula:
            x ⊕ y = ((1+2<x,y>+||y||²)x + (1-||x||²)y) / (1+2<x,y>+||x||²||y||²)
        
        The Möbius addition is the natural addition operation in the
        Poincaré ball that respects the hyperbolic structure.
        
        Args:
            x: Point in Poincaré ball, shape (..., dim)
            y: Point in Poincaré ball, shape (..., dim)
            
        Returns:
            Möbius sum x ⊕ y
        """
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        
        x_norm_sq = np.sum(x**2, axis=-1, keepdims=True)
        y_norm_sq = np.sum(y**2, axis=-1, keepdims=True)
        xy_inner = np.sum(x * y, axis=-1, keepdims=True)
        
        numerator = (1.0 + 2.0*xy_inner + y_norm_sq) * x + (1.0 - x_norm_sq) * y
        denominator = 1.0 + 2.0*xy_inner + x_norm_sq * y_norm_sq + self.eps
        
        result = numerator / denominator
        return self.poincare_projection(result)
    
    def poincare_exp_map(self, x: np.ndarray, v: np.ndarray) -> np.ndarray:
        """
        Exponential map from tangent space to Poincaré ball.
        
        Mathematical formula:
            exp_x(v) = x ⊕ (tanh(λ(x)||v||/2) * v/||v||)
        
        where λ(x) = 2/(1-||x||²) and ⊕ is Möbius addition.
        
        Args:
            x: Base point in Poincaré ball, shape (..., dim)
            v: Tangent vector at x, shape (..., dim)
            
        Returns:
            Point in Poincaré ball reached by exp map
            
        Example:
            >>> model = PoincareModel(dim=2)
            >>> x = np.array([0.0, 0.0])
            >>> v = np.array([0.5, 0.0])
            >>> y = model.poincare_exp_map(x, v)
        """
        x = np.asarray(x, dtype=np.float64)
        v = np.asarray(v, dtype=np.float64)
        
        self._validate_in_ball(x)
        
        # Compute norm of tangent vector
        v_norm = np.linalg.norm(v, axis=-1, keepdims=True)
        
        # Handle zero vector case
        if np.all(v_norm < self.eps):
            return x.copy()
        
        # Compute conformal factor
        lambda_x = self._lambda(x)
        
        # Exponential map formula
        v_normalized = v / (v_norm + self.eps)
        scale = np.tanh(lambda_x[..., np.newaxis] * v_norm / 2.0)
        
        direction = scale * v_normalized
        result = self.mobius_addition(x, direction)
        
        return result
    
    def poincare_log_map(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        Logarithmic map from Poincaré ball to tangent space.
        
        Mathematical formula:
            log_x(y) = (2/λ(x)) * arctanh(||(-x)⊕y||) * ((-x)⊕y)/||(-x)⊕y||
        
        where λ(x) = 2/(1-||x||²) and ⊕ is Möbius addition.
        
        Args:
            x: Base point in Poincaré ball, shape (..., dim)
            y: Target point in Poincaré ball, shape (..., dim)
            
        Returns:
            Tangent vector at x pointing toward y
            
        Example:
            >>> model = PoincareModel(dim=2)
            >>> x = np.array([0.0, 0.0])
            >>> y = np.array([0.5, 0.0])
            >>> v = model.poincare_log_map(x, y)
            >>> z = model.poincare_exp_map(x, v)
            >>> np.allclose(y, z)
            True
        """
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        
        self._validate_in_ball(x)
        self._validate_in_ball(y)
        
        # Handle coincident points
        if np.allclose(x, y, atol=self.eps):
            return np.zeros_like(x)
        
        # Compute (-x) ⊕ y
        neg_x = -x
        direction = self.mobius_addition(neg_x, y)
        
        direction_norm = np.linalg.norm(direction, axis=-1, keepdims=True)
        
        # Compute conformal factor
        lambda_x = self._lambda(x)
        
        # Log map formula
        scale = (2.0 / lambda_x[..., np.newaxis]) * np.arctanh(direction_norm + self.eps)
        v = scale * direction / (direction_norm + self.eps)
        
        return v
    
    def poincare_parallel_transport(self, x: np.ndarray, y: np.ndarray, v: np.ndarray) -> np.ndarray:
        """
        Parallel transport tangent vector from x to y along geodesic.
        
        Uses the formula involving gyrations in gyrovector spaces.
        
        Mathematical formula:
            P_{x→y}(v) = (λ(x)/λ(y)) * gyr[y,-x](v)
        
        where gyr is the gyration operator.
        
        Args:
            x: Source point in Poincaré ball, shape (..., dim)
            y: Target point in Poincaré ball, shape (..., dim)
            v: Tangent vector at x, shape (..., dim)
            
        Returns:
            Parallel transported vector at y
        """
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        v = np.asarray(v, dtype=np.float64)
        
        self._validate_in_ball(x)
        self._validate_in_ball(y)
        
        # Handle same point case
        if np.allclose(x, y, atol=self.eps):
            return v.copy()
        
        # Compute conformal factors
        lambda_x = self._lambda(x)
        lambda_y = self._lambda(y)
        
        # Gyration formula (simplified)
        # For points on a geodesic, parallel transport preserves the
        # direction relative to the geodesic
        neg_x = -x
        u = self.mobius_addition(neg_x, y)
        u_norm_sq = np.sum(u**2, axis=-1, keepdims=True) + self.eps
        
        uv_inner = np.sum(u * v, axis=-1, keepdims=True)
        
        # Gyration operator application
        gyrated = v + 2.0 * uv_inner / u_norm_sq * u
        
        # Scale by conformal factor ratio
        result = (lambda_x / lambda_y)[..., np.newaxis] * gyrated
        
        return result
    
    def poincare_geodesic(self, x: np.ndarray, y: np.ndarray, t: Union[float, np.ndarray]) -> np.ndarray:
        """
        Compute point along geodesic from x to y at parameter t.
        
        Geodesic interpolation in the Poincaré ball. At t=0, returns x;
        at t=1, returns y.
        
        Mathematical formula:
            γ(t) = exp_x(t * log_x(y))
        
        Args:
            x: Start point in Poincaré ball, shape (..., dim)
            y: End point in Poincaré ball, shape (..., dim)
            t: Parameter in [0,1] or array of parameters
            
        Returns:
            Point(s) on geodesic
        """
        t = np.asarray(t, dtype=np.float64)
        
        # Compute log map
        v = self.poincare_log_map(x, y)
        
        # Scale by parameter
        v_scaled = t[..., np.newaxis] * v
        
        # Apply exp map
        return self.poincare_exp_map(x, v_scaled)
    
    def poincare_tangent_projection(self, x: np.ndarray, v: np.ndarray) -> np.ndarray:
        """
        Project vector onto tangent space at x.
        
        In the Poincaré model, the tangent space at any point is simply ℝ^n,
        so this is effectively an identity operation (but included for
        consistency with other models).
        
        Args:
            x: Point in Poincaré ball, shape (..., dim)
            v: Vector in ℝ^n, shape (..., dim)
            
        Returns:
            Projected vector in tangent space at x (same as v)
        """
        return v.copy()
    
    def poincare_mean(self, points: np.ndarray, weights: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Compute Fréchet mean (centroid) of points in Poincaré ball.
        
        The Fréchet mean minimizes the sum of squared distances:
            mean = argmin_p sum_i w_i * d(p, points[i])^2
        
        Uses iterative gradient descent algorithm.
        
        Args:
            points: Array of points in Poincaré ball, shape (n_points, dim)
            weights: Optional weights for each point, shape (n_points,)
            
        Returns:
            Fréchet mean point in Poincaré ball
        """
        points = np.asarray(points, dtype=np.float64)
        n_points = points.shape[0]
        
        if weights is None:
            weights = np.ones(n_points) / n_points
        else:
            weights = np.asarray(weights, dtype=np.float64)
            weights = weights / np.sum(weights)
        
        # Initialize at weighted Euclidean mean (projected to ball)
        mean = np.average(points, axis=0, weights=weights)
        mean = self.poincare_projection(mean)
        
        # Gradient descent
        max_iter = 100
        lr = 0.1
        
        for _ in range(max_iter):
            # Compute gradient (sum of log maps)
            grad = np.zeros(self.dim, dtype=np.float64)
            for i, point in enumerate(points):
                grad += weights[i] * self.poincare_log_map(mean, point)
            
            # Check convergence
            if np.linalg.norm(grad) < self.eps:
                break
            
            # Update mean
            mean = self.poincare_exp_map(mean, lr * grad)
        
        return mean
    
    def poincare_variance(self, points: np.ndarray, mean: Optional[np.ndarray] = None) -> float:
        """
        Compute variance of points around their Fréchet mean.
        
        Mathematical formula:
            var = (1/n) * sum_i d(mean, points[i])^2
        
        Args:
            points: Array of points in Poincaré ball, shape (n_points, dim)
            mean: Pre-computed mean (computed if not provided)
            
        Returns:
            Variance value
        """
        points = np.asarray(points, dtype=np.float64)
        
        if mean is None:
            mean = self.poincare_mean(points)
        
        # Compute squared distances
        distances_sq = self.poincare_distance(mean, points) ** 2
        
        return np.mean(distances_sq)
    
    def poincare_curvature(self, x: np.ndarray) -> float:
        """
        Compute sectional curvature at point x.
        
        For hyperbolic space B^n with standard metric, the sectional
        curvature is constant and equals -1.
        
        Args:
            x: Point in Poincaré ball, shape (dim,)
            
        Returns:
            Sectional curvature (always -1.0 for B^n)
        """
        return -1.0
    
    def poincare_volume(self, points: np.ndarray) -> float:
        """
        Compute hyperbolic volume of simplex formed by points.
        
        Uses distance-based approach similar to Lorentz model.
        
        Args:
            points: Array of n+1 points forming n-simplex, shape (n+1, dim)
            
        Returns:
            Hyperbolic volume of simplex
        """
        points = np.asarray(points, dtype=np.float64)
        n_points = points.shape[0]
        
        # Compute distance matrix
        dist_matrix = np.zeros((n_points, n_points))
        for i in range(n_points):
            for j in range(i + 1, n_points):
                d = self.poincare_distance(points[i], points[j])
                dist_matrix[i, j] = d
                dist_matrix[j, i] = d
        
        # Use similar approach as Lorentz model
        if n_points == 2:
            return dist_matrix[0, 1]
        elif n_points == 3:
            # Triangle area
            a, b, c = dist_matrix[0, 1], dist_matrix[1, 2], dist_matrix[2, 0]
            s = (a + b + c) / 2
            area = 4 * np.arctan(np.sqrt(
                np.sinh(s/2) * np.sinh((s-a)/2) * np.sinh((s-b)/2) * np.sinh((s-c)/2)
            ))
            return area
        else:
            # General case
            return np.abs(np.linalg.det(dist_matrix)) ** 0.5
    
    def poincare_area(self, points: np.ndarray) -> float:
        """
        Compute hyperbolic area of triangle formed by 3 points.
        
        Args:
            points: Array of 3 points forming triangle, shape (3, dim)
            
        Returns:
            Hyperbolic area of triangle
            
        Raises:
            ValueError: If not exactly 3 points provided
        """
        points = np.asarray(points, dtype=np.float64)
        if points.shape[0] != 3:
            raise ValueError(f"Expected 3 points for triangle, got {points.shape[0]}")
        
        return self.poincare_volume(points)
    
    def poincare_to_lorentz(self, x: np.ndarray) -> np.ndarray:
        """
        Convert point from Poincaré ball to Lorentz hyperboloid model.
        
        Mathematical formula:
            L = [1+||x||², x] / (1-||x||²)
        
        This is the inverse of stereographic projection.
        
        Args:
            x: Point in Poincaré ball, shape (..., dim)
            
        Returns:
            Point on Lorentz hyperboloid, shape (..., dim+1)
            
        Example:
            >>> model = PoincareModel(dim=2)
            >>> x = np.array([0.0, 0.0])  # Origin
            >>> L = model.poincare_to_lorentz(x)
            >>> np.allclose(L, [1.0, 0.0, 0.0])
            True
        """
        x = np.asarray(x, dtype=np.float64)
        self._validate_in_ball(x)
        
        x_norm_sq = np.sum(x**2, axis=-1, keepdims=True)
        denominator = 1.0 - x_norm_sq + self.eps
        
        # First component
        x0 = (1.0 + x_norm_sq) / denominator
        
        # Spatial components
        x_spatial = 2.0 * x / denominator
        
        # Concatenate
        lorentz_point = np.concatenate([x0, x_spatial], axis=-1)
        
        return lorentz_point
    
    # Validation methods
    
    def _validate_in_ball(self, x: np.ndarray, tol: Optional[float] = None):
        """
        Validate that point(s) lie in the Poincaré ball.
        
        Checks: ||x|| < 1
        """
        if tol is None:
            tol = self.eps
        
        norm = np.linalg.norm(x, axis=-1)
        if np.any(norm >= 1.0 - tol):
            warnings.warn(
                f"Point not in Poincaré ball: ||x|| = {norm}, must be < 1",
                RuntimeWarning
            )


# Convenience functions for common operations

def poincare_distance(x: np.ndarray, y: np.ndarray, dim: Optional[int] = None) -> Union[float, np.ndarray]:
    """
    Convenience function for computing Poincaré distance.
    
    Args:
        x: Point in Poincaré ball
        y: Point in Poincaré ball
        dim: Dimension (inferred from x if not provided)
        
    Returns:
        Hyperbolic distance
    """
    if dim is None:
        dim = x.shape[-1]
    model = PoincareModel(dim=dim)
    return model.poincare_distance(x, y)


def poincare_exp_map(x: np.ndarray, v: np.ndarray, dim: Optional[int] = None) -> np.ndarray:
    """
    Convenience function for Poincaré exponential map.
    
    Args:
        x: Base point in Poincaré ball
        v: Tangent vector at x
        dim: Dimension (inferred from x if not provided)
        
    Returns:
        Point reached by exponential map
    """
    if dim is None:
        dim = x.shape[-1]
    model = PoincareModel(dim=dim)
    return model.poincare_exp_map(x, v)


def poincare_log_map(x: np.ndarray, y: np.ndarray, dim: Optional[int] = None) -> np.ndarray:
    """
    Convenience function for Poincaré logarithmic map.
    
    Args:
        x: Base point in Poincaré ball
        y: Target point in Poincaré ball
        dim: Dimension (inferred from x if not provided)
        
    Returns:
        Tangent vector at x pointing toward y
    """
    if dim is None:
        dim = x.shape[-1]
    model = PoincareModel(dim=dim)
    return model.poincare_log_map(x, y)
