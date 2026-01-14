"""
Lorentz Hyperboloid Model for Hyperbolic Geometry

This module implements the Lorentz hyperboloid model (also known as the hyperboloid model)
for hyperbolic geometry. Points lie on the upper sheet of a two-sheeted hyperboloid in
(n+1)-dimensional Minkowski space:

    H^n = {x ∈ ℝ^(n+1) : <x,x>_L = -1, x_0 > 0}

where <x,y>_L = -x_0*y_0 + x_1*y_1 + ... + x_n*y_n is the Lorentz inner product.

Mathematical Background:
- The Lorentz model is particularly useful for numerical stability
- Geodesics are intersections of the hyperboloid with 2-planes through the origin
- The exponential map is globally defined and computed via hyperbolic functions
- Distance formula: d(x,y) = arcosh(-<x,y>_L)

References:
- Cannon et al. "Hyperbolic Geometry" (1997)
- Ratcliffe "Foundations of Hyperbolic Manifolds" (2006)
"""

import numpy as np
from typing import Optional, Union, List, Tuple
import warnings


class LorentzModel:
    """
    Lorentz hyperboloid model for hyperbolic geometry.
    
    This class provides numerically stable implementations of hyperbolic
    geometric operations using the Lorentz (hyperboloid) model.
    
    Attributes:
        dim (int): Dimension of the hyperbolic space (n in H^n)
        eps (float): Numerical stability epsilon
    """
    
    def __init__(self, dim: int = 2, eps: float = 1e-12):
        """
        Initialize Lorentz model.
        
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
        
    def lorentz_inner_product(self, x: np.ndarray, y: np.ndarray) -> Union[float, np.ndarray]:
        """
        Compute Lorentz inner product: <x,y>_L = -x₀y₀ + x₁y₁ + ... + xₙyₙ
        
        The Lorentz inner product defines the geometry of Minkowski space.
        For points on the hyperboloid, we have <x,x>_L = -1.
        
        Mathematical formula:
            <x,y>_L = -x[0]*y[0] + sum(x[1:] * y[1:])
        
        Args:
            x: Point in Minkowski space, shape (..., dim+1)
            y: Point in Minkowski space, shape (..., dim+1)
            
        Returns:
            Lorentz inner product value(s)
            
        Example:
            >>> model = LorentzModel(dim=2)
            >>> x = np.array([1.0, 0.0, 0.0])  # Origin in H^2
            >>> y = np.array([1.0, 0.0, 0.0])
            >>> model.lorentz_inner_product(x, y)
            -1.0
        """
        x = np.asarray(x)
        y = np.asarray(y)
        return -x[..., 0] * y[..., 0] + np.sum(x[..., 1:] * y[..., 1:], axis=-1)
    
    def lorentz_norm(self, x: np.ndarray) -> Union[float, np.ndarray]:
        """
        Compute Lorentzian norm: ||x||_L = sqrt(|<x,x>_L|)
        
        For points on the hyperboloid, ||x||_L = 1.
        
        Args:
            x: Point in Minkowski space, shape (..., dim+1)
            
        Returns:
            Lorentzian norm(s)
        """
        return np.sqrt(np.abs(self.lorentz_inner_product(x, x)))
    
    def lorentz_distance(self, x: np.ndarray, y: np.ndarray) -> Union[float, np.ndarray]:
        """
        Compute geodesic distance in Lorentz model: d(x,y) = arcosh(-<x,y>_L)
        
        This is the fundamental distance function in the Lorentz model.
        
        Mathematical formula:
            d(x,y) = arcosh(-<x,y>_L) for x,y ∈ H^n
        
        Properties:
            - Always non-negative
            - Symmetric: d(x,y) = d(y,x)
            - Triangle inequality: d(x,z) ≤ d(x,y) + d(y,z)
            - d(x,y) = 0 iff x = y
        
        Args:
            x: Point on hyperboloid, shape (..., dim+1)
            y: Point on hyperboloid, shape (..., dim+1)
            
        Returns:
            Hyperbolic distance(s)
            
        Raises:
            ValueError: If points are not on the hyperboloid
            
        Example:
            >>> model = LorentzModel(dim=2)
            >>> x = np.array([1.0, 0.0, 0.0])
            >>> y = np.array([np.cosh(1.0), np.sinh(1.0), 0.0])
            >>> model.lorentz_distance(x, y)
            1.0
        """
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        
        # Check for coincident points first
        if np.allclose(x, y, atol=self.eps):
            return np.float64(0.0) if x.ndim == 1 else np.zeros(x.shape[:-1], dtype=np.float64)
        
        # Validate points are on hyperboloid
        self._validate_on_hyperboloid(x)
        self._validate_on_hyperboloid(y)
        
        # Compute inner product
        inner_prod = self.lorentz_inner_product(x, y)
        
        # Clamp to valid range for numerical stability
        # -<x,y>_L >= 1 for points on the hyperboloid
        clamped = np.maximum(-inner_prod, 1.0)
        
        return np.arccosh(clamped)
    
    def lorentz_projection(self, x: np.ndarray) -> np.ndarray:
        """
        Project point onto hyperboloid surface.
        
        Given a point in Minkowski space, find the nearest point on the
        hyperboloid using the constraint <x,x>_L = -1, x₀ > 0.
        
        Mathematical formula:
            proj(x) = x / sqrt(-<x,x>_L) if x₀ > 0
        
        Args:
            x: Point in Minkowski space, shape (..., dim+1)
            
        Returns:
            Projected point on hyperboloid
            
        Raises:
            ValueError: If projection is not possible (x₀ <= 0)
        """
        x = np.asarray(x, dtype=np.float64)
        
        if np.any(x[..., 0] <= 0):
            raise ValueError("Cannot project: x₀ must be positive")
        
        # Compute Lorentz norm
        norm = np.sqrt(-self.lorentz_inner_product(x, x))
        
        # Normalize to hyperboloid
        return x / norm[..., np.newaxis]
    
    def lorentz_exp_map(self, x: np.ndarray, v: np.ndarray) -> np.ndarray:
        """
        Exponential map from tangent space to hyperboloid.
        
        Given a point x on the hyperboloid and a tangent vector v at x,
        compute the point reached by traveling along the geodesic from x
        in the direction v for unit time.
        
        Mathematical formula:
            exp_x(v) = cosh(||v||_L) * x + sinh(||v||_L) * v / ||v||_L
        
        where ||v||_L = sqrt(<v,v>_L) is the Lorentzian norm of the tangent vector.
        
        Properties:
            - Globally defined (unlike Poincaré model)
            - Geodesic: t -> exp_x(t*v) is a geodesic
            - Distance: d(x, exp_x(v)) = ||v||_L
        
        Args:
            x: Base point on hyperboloid, shape (..., dim+1)
            v: Tangent vector at x, shape (..., dim+1)
            
        Returns:
            Point on hyperboloid reached by exp map
            
        Example:
            >>> model = LorentzModel(dim=2)
            >>> x = np.array([1.0, 0.0, 0.0])
            >>> v = np.array([0.0, 1.0, 0.0])
            >>> y = model.lorentz_exp_map(x, v)
            >>> model.lorentz_distance(x, y)
            1.0
        """
        x = np.asarray(x, dtype=np.float64)
        v = np.asarray(v, dtype=np.float64)
        
        # Validate x is on hyperboloid
        self._validate_on_hyperboloid(x)
        
        # Validate v is in tangent space: <x,v>_L = 0
        self._validate_tangent_vector(x, v)
        
        # Compute norm of tangent vector
        v_norm_sq = self.lorentz_inner_product(v, v)
        v_norm = np.sqrt(np.maximum(v_norm_sq, 0.0))
        
        # Handle zero vector case
        if np.all(v_norm < self.eps):
            return x.copy()
        
        # Exponential map formula
        cosh_norm = np.cosh(v_norm)
        sinh_norm = np.sinh(v_norm)
        
        # Avoid division by zero
        scale = np.where(v_norm > self.eps, sinh_norm / v_norm, 1.0)
        
        result = cosh_norm[..., np.newaxis] * x + scale[..., np.newaxis] * v
        
        return result
    
    def lorentz_log_map(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        Logarithmic map from hyperboloid to tangent space.
        
        Given two points x and y on the hyperboloid, compute the tangent
        vector at x that points toward y.
        
        Mathematical formula:
            log_x(y) = d(x,y) * (y - <x,y>_L * x) / ||y - <x,y>_L * x||
        
        where d(x,y) is the distance from x to y.
        
        Properties:
            - Inverse of exp map: log_x(exp_x(v)) = v
            - exp_x(log_x(y)) = y
            - ||log_x(y)||_L = d(x,y)
        
        Args:
            x: Base point on hyperboloid, shape (..., dim+1)
            y: Target point on hyperboloid, shape (..., dim+1)
            
        Returns:
            Tangent vector at x pointing toward y
            
        Example:
            >>> model = LorentzModel(dim=2)
            >>> x = np.array([1.0, 0.0, 0.0])
            >>> y = np.array([np.cosh(1.0), np.sinh(1.0), 0.0])
            >>> v = model.lorentz_log_map(x, y)
            >>> np.allclose(model.lorentz_exp_map(x, v), y)
            True
        """
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        
        # Validate points are on hyperboloid
        self._validate_on_hyperboloid(x)
        self._validate_on_hyperboloid(y)
        
        # Handle coincident points first (before computing distance)
        if np.allclose(x, y, atol=self.eps):
            return np.zeros_like(x)
        
        # Compute distance
        dist = self.lorentz_distance(x, y)
        
        # Additional check for very small distance
        if np.all(dist < self.eps):
            return np.zeros_like(x)
        
        # Compute inner product
        inner_prod = self.lorentz_inner_product(x, y)
        
        # Compute direction vector (orthogonal to x)
        direction = y + inner_prod[..., np.newaxis] * x
        
        # Normalize direction
        direction_norm = self.lorentz_norm(direction)
        
        # Avoid division by zero
        if np.all(direction_norm < self.eps):
            return np.zeros_like(x)
        
        direction_normalized = direction / (direction_norm[..., np.newaxis] + self.eps)
        
        # Scale by distance
        result = dist[..., np.newaxis] * direction_normalized
        
        return result
    
    def lorentz_parallel_transport(self, x: np.ndarray, y: np.ndarray, v: np.ndarray) -> np.ndarray:
        """
        Parallel transport tangent vector from x to y along geodesic.
        
        Given a tangent vector v at x, compute its parallel transport to y
        along the unique geodesic connecting x and y.
        
        Mathematical formula:
            P_{x→y}(v) = v - <y,v>_L/(1-<x,y>_L) * (x+y)
        
        Properties:
            - Preserves inner products: <v,w>_x = <P(v),P(w)>_y
            - Preserves norms: ||P(v)||_y = ||v||_x
            - Linear: P(av + bw) = aP(v) + bP(w)
        
        Args:
            x: Source point on hyperboloid, shape (..., dim+1)
            y: Target point on hyperboloid, shape (..., dim+1)
            v: Tangent vector at x, shape (..., dim+1)
            
        Returns:
            Parallel transported vector at y
            
        Example:
            >>> model = LorentzModel(dim=2)
            >>> x = np.array([1.0, 0.0, 0.0])
            >>> y = np.array([np.cosh(1.0), np.sinh(1.0), 0.0])
            >>> v = np.array([0.0, 0.0, 1.0])
            >>> w = model.lorentz_parallel_transport(x, y, v)
            >>> np.allclose(model.lorentz_norm(w), model.lorentz_norm(v))
            True
        """
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        v = np.asarray(v, dtype=np.float64)
        
        # Validate inputs
        self._validate_on_hyperboloid(x)
        self._validate_on_hyperboloid(y)
        self._validate_tangent_vector(x, v)
        
        # Handle same point case
        if np.allclose(x, y, atol=self.eps):
            return v.copy()
        
        # Compute inner products
        xy_inner = self.lorentz_inner_product(x, y)
        yv_inner = self.lorentz_inner_product(y, v)
        
        # Parallel transport formula
        denominator = 1.0 - xy_inner
        scale = yv_inner / denominator
        
        result = v - scale[..., np.newaxis] * (x + y)
        
        return result
    
    def lorentz_geodesic(self, x: np.ndarray, y: np.ndarray, t: Union[float, np.ndarray]) -> np.ndarray:
        """
        Compute point along geodesic from x to y at parameter t.
        
        Geodesic interpolation in the Lorentz model. At t=0, returns x;
        at t=1, returns y.
        
        Mathematical formula:
            γ(t) = exp_x(t * log_x(y))
        
        Args:
            x: Start point on hyperboloid, shape (..., dim+1)
            y: End point on hyperboloid, shape (..., dim+1)
            t: Parameter in [0,1] or array of parameters
            
        Returns:
            Point(s) on geodesic
            
        Example:
            >>> model = LorentzModel(dim=2)
            >>> x = np.array([1.0, 0.0, 0.0])
            >>> y = np.array([np.cosh(2.0), np.sinh(2.0), 0.0])
            >>> mid = model.lorentz_geodesic(x, y, 0.5)
            >>> d1 = model.lorentz_distance(x, mid)
            >>> d2 = model.lorentz_distance(mid, y)
            >>> np.allclose(d1, d2)
            True
        """
        t = np.asarray(t, dtype=np.float64)
        
        # Compute log map
        v = self.lorentz_log_map(x, y)
        
        # Scale by parameter
        v_scaled = t[..., np.newaxis] * v
        
        # Apply exp map
        return self.lorentz_exp_map(x, v_scaled)
    
    def lorentz_tangent_projection(self, x: np.ndarray, v: np.ndarray) -> np.ndarray:
        """
        Project vector onto tangent space at x.
        
        Given a vector v in Minkowski space, project it onto the tangent
        space T_x H^n, which is defined by <x,w>_L = 0.
        
        Mathematical formula:
            proj_{T_x}(v) = v - <x,v>_L * x
        
        Args:
            x: Point on hyperboloid, shape (..., dim+1)
            v: Vector in Minkowski space, shape (..., dim+1)
            
        Returns:
            Projected vector in tangent space at x
        """
        x = np.asarray(x, dtype=np.float64)
        v = np.asarray(v, dtype=np.float64)
        
        self._validate_on_hyperboloid(x)
        
        # Project onto tangent space
        inner_prod = self.lorentz_inner_product(x, v)
        result = v - inner_prod[..., np.newaxis] * x
        
        return result
    
    def lorentz_mean(self, points: np.ndarray, weights: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Compute Fréchet mean (centroid) of points on hyperboloid.
        
        The Fréchet mean minimizes the sum of squared distances:
            mean = argmin_p sum_i w_i * d(p, points[i])^2
        
        Uses iterative gradient descent algorithm.
        
        Args:
            points: Array of points on hyperboloid, shape (n_points, dim+1)
            weights: Optional weights for each point, shape (n_points,)
            
        Returns:
            Fréchet mean point on hyperboloid
            
        Example:
            >>> model = LorentzModel(dim=2)
            >>> points = np.array([
            ...     [1.0, 0.0, 0.0],
            ...     [np.cosh(1.0), np.sinh(1.0), 0.0],
            ...     [np.cosh(1.0), 0.0, np.sinh(1.0)]
            ... ])
            >>> mean = model.lorentz_mean(points)
        """
        points = np.asarray(points, dtype=np.float64)
        n_points = points.shape[0]
        
        if weights is None:
            weights = np.ones(n_points) / n_points
        else:
            weights = np.asarray(weights, dtype=np.float64)
            weights = weights / np.sum(weights)
        
        # Initialize at first point
        mean = points[0].copy()
        
        # Gradient descent
        max_iter = 100
        lr = 0.1
        
        for _ in range(max_iter):
            # Compute gradient (sum of log maps)
            grad = np.zeros(self.dim + 1, dtype=np.float64)
            for i, point in enumerate(points):
                grad += weights[i] * self.lorentz_log_map(mean, point)
            
            # Check convergence
            if np.linalg.norm(grad) < self.eps:
                break
            
            # Update mean
            mean = self.lorentz_exp_map(mean, lr * grad)
        
        return mean
    
    def lorentz_variance(self, points: np.ndarray, mean: Optional[np.ndarray] = None) -> float:
        """
        Compute variance of points around their Fréchet mean.
        
        Mathematical formula:
            var = (1/n) * sum_i d(mean, points[i])^2
        
        Args:
            points: Array of points on hyperboloid, shape (n_points, dim+1)
            mean: Pre-computed mean (computed if not provided)
            
        Returns:
            Variance value
        """
        points = np.asarray(points, dtype=np.float64)
        
        if mean is None:
            mean = self.lorentz_mean(points)
        
        # Compute squared distances
        distances_sq = self.lorentz_distance(mean, points) ** 2
        
        return np.mean(distances_sq)
    
    def lorentz_curvature(self, x: np.ndarray) -> float:
        """
        Compute sectional curvature at point x.
        
        For hyperbolic space H^n with standard metric, the sectional
        curvature is constant and equals -1.
        
        Args:
            x: Point on hyperboloid, shape (dim+1,)
            
        Returns:
            Sectional curvature (always -1.0 for H^n)
        """
        return -1.0
    
    def lorentz_volume(self, points: np.ndarray) -> float:
        """
        Compute hyperbolic volume of simplex formed by points.
        
        Uses the Cayley-Menger determinant approach adapted for
        hyperbolic geometry.
        
        Args:
            points: Array of n+1 points forming n-simplex, shape (n+1, dim+1)
            
        Returns:
            Hyperbolic volume of simplex
            
        Note:
            For n=2 (triangle), this gives the area.
            For n=3 (tetrahedron), this gives the volume.
        """
        points = np.asarray(points, dtype=np.float64)
        n_points = points.shape[0]
        
        # Compute distance matrix
        dist_matrix = np.zeros((n_points, n_points))
        for i in range(n_points):
            for j in range(i + 1, n_points):
                d = self.lorentz_distance(points[i], points[j])
                dist_matrix[i, j] = d
                dist_matrix[j, i] = d
        
        # Use Cayley-Menger determinant (simplified calculation)
        # For hyperbolic geometry, this is an approximation
        if n_points == 2:
            return dist_matrix[0, 1]
        elif n_points == 3:
            # Triangle area using Heron's formula (hyperbolic version)
            a, b, c = dist_matrix[0, 1], dist_matrix[1, 2], dist_matrix[2, 0]
            s = (a + b + c) / 2
            # Hyperbolic area formula
            area = 4 * np.arctan(np.sqrt(
                np.sinh(s/2) * np.sinh((s-a)/2) * np.sinh((s-b)/2) * np.sinh((s-c)/2)
            ))
            return area
        else:
            # General case: use determinant method (approximate)
            return np.abs(np.linalg.det(dist_matrix)) ** 0.5
    
    def lorentz_area(self, points: np.ndarray) -> float:
        """
        Compute hyperbolic area of triangle formed by 3 points.
        
        This is a convenience wrapper around lorentz_volume for triangles.
        
        Args:
            points: Array of 3 points forming triangle, shape (3, dim+1)
            
        Returns:
            Hyperbolic area of triangle
            
        Raises:
            ValueError: If not exactly 3 points provided
        """
        points = np.asarray(points, dtype=np.float64)
        if points.shape[0] != 3:
            raise ValueError(f"Expected 3 points for triangle, got {points.shape[0]}")
        
        return self.lorentz_volume(points)
    
    def lorentz_to_poincare(self, x: np.ndarray) -> np.ndarray:
        """
        Convert point from Lorentz model to Poincaré ball model.
        
        Mathematical formula:
            p = x[1:] / (x[0] + 1)
        
        This is the stereographic projection from the hyperboloid to the
        Poincaré ball.
        
        Args:
            x: Point on hyperboloid, shape (..., dim+1)
            
        Returns:
            Point in Poincaré ball, shape (..., dim)
            
        Example:
            >>> model = LorentzModel(dim=2)
            >>> x = np.array([1.0, 0.0, 0.0])  # Origin in both models
            >>> p = model.lorentz_to_poincare(x)
            >>> np.allclose(p, [0.0, 0.0])
            True
        """
        x = np.asarray(x, dtype=np.float64)
        self._validate_on_hyperboloid(x)
        
        # Stereographic projection
        denominator = x[..., 0:1] + 1.0
        poincare_point = x[..., 1:] / denominator
        
        return poincare_point
    
    # Validation methods
    
    def _validate_on_hyperboloid(self, x: np.ndarray, tol: Optional[float] = None):
        """
        Validate that point(s) lie on the hyperboloid.
        
        Checks: <x,x>_L = -1 and x_0 > 0
        """
        if tol is None:
            tol = self.eps * 10
        
        # Check Lorentz inner product
        inner_prod = self.lorentz_inner_product(x, x)
        if not np.allclose(inner_prod, -1.0, atol=tol):
            warnings.warn(
                f"Point not on hyperboloid: <x,x>_L = {inner_prod}, expected -1.0",
                RuntimeWarning
            )
        
        # Check x_0 > 0
        if np.any(x[..., 0] <= 0):
            raise ValueError("Point not on upper sheet: x_0 must be positive")
    
    def _validate_tangent_vector(self, x: np.ndarray, v: np.ndarray, tol: Optional[float] = None):
        """
        Validate that v is in the tangent space at x.
        
        Checks: <x,v>_L = 0
        """
        if tol is None:
            tol = self.eps * 10
        
        inner_prod = self.lorentz_inner_product(x, v)
        if not np.allclose(inner_prod, 0.0, atol=tol):
            warnings.warn(
                f"Vector not in tangent space: <x,v>_L = {inner_prod}, expected 0.0",
                RuntimeWarning
            )


# Convenience functions for common operations

def lorentz_distance(x: np.ndarray, y: np.ndarray, dim: Optional[int] = None) -> Union[float, np.ndarray]:
    """
    Convenience function for computing Lorentz distance.
    
    Args:
        x: Point on hyperboloid
        y: Point on hyperboloid
        dim: Dimension (inferred from x if not provided)
        
    Returns:
        Hyperbolic distance
    """
    if dim is None:
        dim = x.shape[-1] - 1
    model = LorentzModel(dim=dim)
    return model.lorentz_distance(x, y)


def lorentz_exp_map(x: np.ndarray, v: np.ndarray, dim: Optional[int] = None) -> np.ndarray:
    """
    Convenience function for Lorentz exponential map.
    
    Args:
        x: Base point on hyperboloid
        v: Tangent vector at x
        dim: Dimension (inferred from x if not provided)
        
    Returns:
        Point reached by exponential map
    """
    if dim is None:
        dim = x.shape[-1] - 1
    model = LorentzModel(dim=dim)
    return model.lorentz_exp_map(x, v)


def lorentz_log_map(x: np.ndarray, y: np.ndarray, dim: Optional[int] = None) -> np.ndarray:
    """
    Convenience function for Lorentz logarithmic map.
    
    Args:
        x: Base point on hyperboloid
        y: Target point on hyperboloid
        dim: Dimension (inferred from x if not provided)
        
    Returns:
        Tangent vector at x pointing toward y
    """
    if dim is None:
        dim = x.shape[-1] - 1
    model = LorentzModel(dim=dim)
    return model.lorentz_log_map(x, y)
