"""
Hyperbolic Metrics - Distance and metric calculations for hyperbolic geometry.

Implements distance formulas for all supported hyperbolic models.
"""
import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class HyperbolicMetrics:
    """
    Hyperbolic distance and metric calculations.

    Supports:
    - Poincaré disk model
    - Hyperboloid model
    - Klein model
    - Upper half-space model
    """

    def __init__(self):
        self._epsilon = 1e-10  # Numerical stability

    def poincare_distance(self, z1: Tuple[float, float], z2: Tuple[float, float]) -> float:
        """
        Compute hyperbolic distance in Poincaré disk model.

        Formula: d(z1, z2) = arcosh(1 + 2|z1 - z2|²/((1 - |z1|²)(1 - |z2|²)))

        Args:
            z1: First point (x, y)
            z2: Second point (x, y)

        Returns:
            Hyperbolic distance
        """
        x1, y1 = z1
        x2, y2 = z2

        # Compute |z1|² and |z2|²
        norm1_sq = x1**2 + y1**2
        norm2_sq = x2**2 + y2**2

        # Check bounds (must be < 1 for Poincaré disk)
        if norm1_sq >= 1.0 - self._epsilon or norm2_sq >= 1.0 - self._epsilon:
            logger.warning(f"Point outside Poincaré disk: {z1}, {z2}")
            return float('inf')

        # Compute |z1 - z2|²
        diff_sq = (x1 - x2)**2 + (y1 - y2)**2

        # Compute distance
        numerator = 2 * diff_sq
        denominator = (1 - norm1_sq) * (1 - norm2_sq)

        if denominator < self._epsilon:
            return float('inf')

        arg = 1 + numerator / denominator

        # Numerical stability
        if arg < 1.0:
            return 0.0

        return np.arccosh(arg)

    def hyperboloid_distance(self, p1: Tuple, p2: Tuple) -> float:
        """
        Compute hyperbolic distance in hyperboloid model.

        Formula: d(p1, p2) = arcosh(-⟨p1, p2⟩_L)
        where ⟨·,·⟩_L is the Lorentzian inner product

        Args:
            p1: First point (t, x, y, z) or (t, x, y)
            p2: Second point (t, x, y, z) or (t, x, y)

        Returns:
            Hyperbolic distance
        """
        # Convert to numpy arrays
        p1_arr = np.array(p1)
        p2_arr = np.array(p2)

        # Lorentzian inner product: -t1*t2 + x1*x2 + y1*y2 + z1*z2
        # First component is timelike (negative), rest are spacelike (positive)
        inner_product = -p1_arr[0] * p2_arr[0] + np.sum(p1_arr[1:] * p2_arr[1:])

        # Distance formula
        arg = -inner_product

        if arg < 1.0:
            # Points are too close or invalid
            return 0.0

        return np.arccosh(arg)

    def klein_distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """
        Compute hyperbolic distance in Klein model.

        Formula: d(p1, p2) = arcosh((1 - p1·p2) / sqrt((1-|p1|²)(1-|p2|²)))

        Args:
            p1: First point (x, y)
            p2: Second point (x, y)

        Returns:
            Hyperbolic distance
        """
        x1, y1 = p1
        x2, y2 = p2

        # Compute norms
        norm1_sq = x1**2 + y1**2
        norm2_sq = x2**2 + y2**2

        # Check bounds
        if norm1_sq >= 1.0 - self._epsilon or norm2_sq >= 1.0 - self._epsilon:
            logger.warning(f"Point outside Klein disk: {p1}, {p2}")
            return float('inf')

        # Dot product
        dot_product = x1 * x2 + y1 * y2

        # Distance formula
        numerator = 1 - dot_product
        denominator = np.sqrt((1 - norm1_sq) * (1 - norm2_sq))

        if denominator < self._epsilon:
            return float('inf')

        arg = numerator / denominator

        if arg < 1.0:
            return 0.0

        return np.arccosh(arg)

    def upper_half_space_distance(
        self,
        p1: Tuple[float, float],
        p2: Tuple[float, float]
    ) -> float:
        """
        Compute hyperbolic distance in upper half-space model.

        Formula: d(p1, p2) = arcosh(1 + |p1-p2|²/(2*y1*y2))
        where y is the height coordinate

        Args:
            p1: First point (x, y) where y > 0
            p2: Second point (x, y) where y > 0

        Returns:
            Hyperbolic distance
        """
        x1, y1 = p1
        x2, y2 = p2

        # Check that y > 0
        if y1 <= self._epsilon or y2 <= self._epsilon:
            logger.warning(f"Invalid upper half-space point: {p1}, {p2}")
            return float('inf')

        # Euclidean distance squared
        euclidean_sq = (x1 - x2)**2 + (y1 - y2)**2

        # Distance formula
        arg = 1 + euclidean_sq / (2 * y1 * y2)

        if arg < 1.0:
            return 0.0

        return np.arccosh(arg)

    def poincare_metric_tensor(self, z: Tuple[float, float]) -> np.ndarray:
        """
        Compute metric tensor at point in Poincaré disk.

        Metric: g = 4/(1-|z|²)² * I

        Args:
            z: Point (x, y)

        Returns:
            2x2 metric tensor
        """
        x, y = z
        norm_sq = x**2 + y**2

        if norm_sq >= 1.0 - self._epsilon:
            # At boundary, metric blows up
            factor = float('inf')
        else:
            factor = 4.0 / (1 - norm_sq)**2

        return factor * np.eye(2)

    def hyperboloid_metric_tensor(self, p: Tuple) -> np.ndarray:
        """
        Compute metric tensor at point in hyperboloid model.

        Metric: diag(-1, 1, 1, 1) (Lorentzian)

        Args:
            p: Point (t, x, y, z)

        Returns:
            4x4 metric tensor
        """
        dim = len(p)
        metric = np.eye(dim)
        metric[0, 0] = -1  # Timelike component
        return metric

    def christoffel_symbols(
        self,
        z: Tuple[float, float],
        model: str = "poincare"
    ) -> np.ndarray:
        """
        Compute Christoffel symbols for geodesic equations.

        Args:
            z: Point coordinates
            model: Geometry model

        Returns:
            Christoffel symbols Γ^k_ij
        """
        if model == "poincare":
            x, y = z
            norm_sq = x**2 + y**2

            if norm_sq >= 1.0 - self._epsilon:
                # Near boundary
                return np.zeros((2, 2, 2))

            # Simplified Christoffel symbols for Poincaré disk
            factor = 2.0 / (1 - norm_sq)

            gamma = np.zeros((2, 2, 2))
            gamma[0, 0, 0] = factor * x
            gamma[0, 0, 1] = factor * y
            gamma[0, 1, 0] = factor * y
            gamma[1, 0, 1] = factor * x
            gamma[1, 1, 1] = factor * y

            return gamma

        return np.zeros((2, 2, 2))

    def get_status(self) -> dict:
        """Get metrics module status."""
        return {
            "epsilon": self._epsilon,
            "supported_models": [
                "poincare_disk",
                "hyperboloid",
                "klein",
                "upper_half_space"
            ]
        }
