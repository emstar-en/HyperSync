"""
Projection Registry - Convert between hyperbolic models.
"""
import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class ProjectionRegistry:
    """Project points between different hyperbolic models."""

    def __init__(self):
        self._epsilon = 1e-10

    def project(
        self,
        point: Tuple,
        from_model: str,
        to_model: str
    ) -> Tuple:
        """
        Project point from one model to another.

        Args:
            point: Point in source model
            from_model: Source model name
            to_model: Target model name

        Returns:
            Point in target model
        """
        if from_model == to_model:
            return point

        # Route through intermediate models if needed
        if from_model == "poincare_disk" and to_model == "hyperboloid":
            return self.poincare_to_hyperboloid(point)
        elif from_model == "hyperboloid" and to_model == "poincare_disk":
            return self.hyperboloid_to_poincare(point)
        elif from_model == "poincare_disk" and to_model == "klein":
            return self.poincare_to_klein(point)
        elif from_model == "klein" and to_model == "poincare_disk":
            return self.klein_to_poincare(point)
        else:
            # Multi-hop projection
            if from_model == "klein" and to_model == "hyperboloid":
                poincare = self.klein_to_poincare(point)
                return self.poincare_to_hyperboloid(poincare)
            elif from_model == "hyperboloid" and to_model == "klein":
                poincare = self.hyperboloid_to_poincare(point)
                return self.poincare_to_klein(poincare)

        raise ValueError(f"Projection not implemented: {from_model} -> {to_model}")

    def poincare_to_hyperboloid(self, z: Tuple[float, float]) -> Tuple:
        """
        Project from Poincaré disk to hyperboloid.

        Formula: (t, x, y) = ((1+|z|²)/(1-|z|²), 2x/(1-|z|²), 2y/(1-|z|²))
        """
        x, y = z
        norm_sq = x**2 + y**2

        if norm_sq >= 1.0 - self._epsilon:
            logger.warning(f"Point near boundary: {z}")
            norm_sq = 1.0 - self._epsilon

        denom = 1 - norm_sq
        t = (1 + norm_sq) / denom
        hx = 2 * x / denom
        hy = 2 * y / denom

        return (t, hx, hy)

    def hyperboloid_to_poincare(self, p: Tuple) -> Tuple[float, float]:
        """
        Project from hyperboloid to Poincaré disk.

        Formula: (x, y) = (x/(1+t), y/(1+t))
        """
        if len(p) < 3:
            raise ValueError("Hyperboloid point must have at least 3 coordinates")

        t, x, y = p[0], p[1], p[2]

        if t < -1 + self._epsilon:
            logger.warning(f"Invalid hyperboloid point: {p}")
            t = -1 + self._epsilon

        denom = 1 + t
        if denom < self._epsilon:
            return (0.0, 0.0)

        px = x / denom
        py = y / denom

        return (px, py)

    def poincare_to_klein(self, z: Tuple[float, float]) -> Tuple[float, float]:
        """
        Project from Poincaré disk to Klein disk.

        Formula: w = 2z/(1+|z|²)
        """
        x, y = z
        norm_sq = x**2 + y**2

        denom = 1 + norm_sq
        kx = 2 * x / denom
        ky = 2 * y / denom

        return (kx, ky)

    def klein_to_poincare(self, w: Tuple[float, float]) -> Tuple[float, float]:
        """
        Project from Klein disk to Poincaré disk.

        Formula: z = w/(1+sqrt(1-|w|²))
        """
        x, y = w
        norm_sq = x**2 + y**2

        if norm_sq >= 1.0 - self._epsilon:
            logger.warning(f"Point near Klein boundary: {w}")
            norm_sq = 1.0 - self._epsilon

        sqrt_term = np.sqrt(1 - norm_sq)
        denom = 1 + sqrt_term

        px = x / denom
        py = y / denom

        return (px, py)
