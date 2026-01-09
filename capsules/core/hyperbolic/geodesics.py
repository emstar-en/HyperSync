"""
Geodesic Computer - Compute geodesic paths in hyperbolic space.
"""
import numpy as np
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)


class GeodesicComputer:
    """Compute geodesic paths in various hyperbolic models."""

    def poincare_geodesic(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        num_points: int = 50
    ) -> List[Tuple[float, float]]:
        """
        Compute geodesic in Poincaré disk.

        Geodesics are circular arcs orthogonal to the boundary.
        """
        x1, y1 = start
        x2, y2 = end

        # Special case: geodesic through origin is a straight line
        if abs(x1 * y2 - x2 * y1) < 1e-10:
            t_values = np.linspace(0, 1, num_points)
            return [(x1 + t * (x2 - x1), y1 + t * (y2 - y1)) for t in t_values]

        # General case: find center and radius of circular arc
        # Solve for circle passing through start, end, orthogonal to unit circle

        # Simplified: use linear interpolation in hyperbolic coordinates
        # (More accurate implementation would compute actual circular arc)
        t_values = np.linspace(0, 1, num_points)
        path = []

        for t in t_values:
            # Hyperbolic interpolation
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)

            # Normalize to stay in disk
            norm = np.sqrt(x**2 + y**2)
            if norm >= 0.99:
                x = x * 0.99 / norm
                y = y * 0.99 / norm

            path.append((x, y))

        return path

    def hyperboloid_geodesic(
        self,
        start: Tuple,
        end: Tuple,
        num_points: int = 50
    ) -> List[Tuple]:
        """
        Compute geodesic in hyperboloid model.

        Geodesics are intersections of hyperboloid with planes through origin.
        """
        p1 = np.array(start)
        p2 = np.array(end)

        # Compute Lorentzian inner product
        def lorentz_inner(a, b):
            return -a[0] * b[0] + np.sum(a[1:] * b[1:])

        # Distance parameter
        d = np.arccosh(-lorentz_inner(p1, p2))

        if d < 1e-10:
            return [tuple(p1) for _ in range(num_points)]

        # Parametrize geodesic
        t_values = np.linspace(0, 1, num_points)
        path = []

        for t in t_values:
            s = t * d
            # Geodesic formula: γ(s) = cosh(s)*p1 + sinh(s)*v
            # where v is the initial velocity
            point = np.cosh(s) * p1 + np.sinh(s) * (p2 - np.cosh(d) * p1) / np.sinh(d)
            path.append(tuple(point))

        return path

    def parallel_transport(
        self,
        vector: Tuple,
        along_geodesic: List[Tuple],
        model: str = "poincare_disk"
    ) -> List[Tuple]:
        """
        Parallel transport vector along geodesic.

        Args:
            vector: Initial vector
            along_geodesic: Geodesic path
            model: Geometry model

        Returns:
            Transported vectors at each point
        """
        if not along_geodesic:
            return []

        # Simplified implementation
        # Full implementation would solve parallel transport equations
        transported = [vector]

        for i in range(1, len(along_geodesic)):
            # Keep vector constant in tangent space (simplified)
            transported.append(vector)

        return transported
