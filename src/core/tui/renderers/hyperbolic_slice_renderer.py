"""
Hyperbolic Slice Renderer

Multi-mode hyperbolic space visualization with full geometry and curvature domain support.

Supported geometries:
1. Poincaré disk
2. Hyperboloid
3. Black-hole lens (Penrose)
4. Wormhole throat
5. Fiber bundle
6. Klein disk
7. Upper half-plane
8. Beltrami-Klein
9. Hemisphere
10. Lorentz

Curvature domains:
- Positive (spherical)
- Zero (flat)
- Negative (hyperbolic)
- Mixed (transition regions)
"""

import math
import logging
from typing import Dict, Any, List, Tuple, Optional


logger = logging.getLogger(__name__)


class HyperbolicSliceRenderer:
    """
    Hyperbolic slice renderer with full geometry support.
    """

    def __init__(self):
        self.geometry_modes = [
            "poincare_disk",
            "hyperboloid",
            "black_hole_lens",
            "wormhole_throat",
            "fiber_bundle",
            "klein_disk",
            "upper_half_plane",
            "beltrami_klein",
            "hemisphere",
            "lorentz"
        ]
        logger.info("HyperbolicSliceRenderer initialized with 10 geometry modes")

    def render(
        self,
        buffer: Any,
        position: Any,
        points: List[Dict[str, float]],
        geometry_mode: str,
        curvature_domain: str,
        capabilities: Dict[str, Any]
    ):
        """
        Render hyperbolic slice.

        Args:
            buffer: Render buffer
            position: Panel position
            points: Points to render
            geometry_mode: Geometry mode
            curvature_domain: Curvature domain (positive, zero, negative, mixed)
            capabilities: Terminal capabilities
        """
        if geometry_mode not in self.geometry_modes:
            logger.warning(f"Unknown geometry mode: {geometry_mode}")
            geometry_mode = "poincare_disk"

        # Dispatch to appropriate renderer
        renderer_map = {
            "poincare_disk": self._render_poincare_disk,
            "hyperboloid": self._render_hyperboloid,
            "black_hole_lens": self._render_black_hole_lens,
            "wormhole_throat": self._render_wormhole_throat,
            "fiber_bundle": self._render_fiber_bundle,
            "klein_disk": self._render_klein_disk,
            "upper_half_plane": self._render_upper_half_plane,
            "beltrami_klein": self._render_beltrami_klein,
            "hemisphere": self._render_hemisphere,
            "lorentz": self._render_lorentz
        }

        renderer = renderer_map.get(geometry_mode, self._render_poincare_disk)
        renderer(buffer, position, points, curvature_domain, capabilities)

    def _render_poincare_disk(self, buffer, position, points, curvature, capabilities):
        """Render Poincaré disk projection."""
        row, col, height, width = position.row, position.col, position.height, position.width
        center_row = row + height // 2
        center_col = col + width // 2
        radius = min(height // 2 - 2, width // 4 - 2)

        # Draw boundary circle
        for angle in range(0, 360, 10):
            rad = math.radians(angle)
            r = center_row + int(radius * math.sin(rad))
            c = center_col + int(radius * 2 * math.cos(rad))
            if row < r < row + height and col < c < col + width:
                buffer.write(r, c, "·" if capabilities.get("unicode_support") else ".")

        # Plot points with curvature coloring
        for point in points:
            x, y = point.get("x", 0.0), point.get("y", 0.0)
            screen_row = center_row + int(y * radius)
            screen_col = center_col + int(x * radius * 2)

            if row < screen_row < row + height and col < screen_col < col + width:
                marker = self._get_curvature_marker(curvature, capabilities)
                buffer.write(screen_row, screen_col, marker)

    def _render_hyperboloid(self, buffer, position, points, curvature, capabilities):
        """Render hyperboloid model."""
        row, col, height, width = position.row, position.col, position.height, position.width
        center_row = row + height // 2
        center_col = col + width // 2

        # Draw hyperboloid outline
        for i in range(height - 4):
            offset = int(math.sqrt(i + 1) * 2)
            current_row = row + 2 + i

            if row < current_row < row + height:
                if col < center_col - offset < col + width:
                    buffer.write(current_row, center_col - offset, "|")
                if col < center_col + offset < col + width:
                    buffer.write(current_row, center_col + offset, "|")

        # Plot points
        for point in points:
            x, y, z = point.get("x", 0.0), point.get("y", 0.0), point.get("z", 0.0)
            screen_row = center_row + int(z * (height // 4))
            screen_col = center_col + int(x * (width // 4))

            if row < screen_row < row + height and col < screen_col < col + width:
                marker = self._get_curvature_marker(curvature, capabilities)
                buffer.write(screen_row, screen_col, marker)

    def _render_black_hole_lens(self, buffer, position, points, curvature, capabilities):
        """Render black-hole lens (Penrose diagram)."""
        row, col, height, width = position.row, position.col, position.height, position.width
        center_row = row + height // 2
        center_col = col + width // 2

        # Draw light cone boundaries
        for i in range(height - 4):
            offset = i
            current_row = row + 2 + i

            if row < current_row < row + height:
                if col < center_col - offset < col + width:
                    buffer.write(current_row, center_col - offset, "/")
                if col < center_col + offset < col + width:
                    buffer.write(current_row, center_col + offset, "\\")

        # Plot points with gravitational lensing
        for point in points:
            x, y = point.get("x", 0.0), point.get("y", 0.0)

            # Apply lensing distortion
            r = math.sqrt(x*x + y*y)
            if r > 0:
                lens_factor = 1.0 / (1.0 + r)
                x *= lens_factor
                y *= lens_factor

            screen_row = center_row + int(y * (height // 4))
            screen_col = center_col + int(x * (width // 4))

            if row < screen_row < row + height and col < screen_col < col + width:
                marker = self._get_curvature_marker(curvature, capabilities)
                buffer.write(screen_row, screen_col, marker)

    def _render_wormhole_throat(self, buffer, position, points, curvature, capabilities):
        """Render wormhole throat geometry."""
        row, col, height, width = position.row, position.col, position.height, position.width
        center_row = row + height // 2
        center_col = col + width // 2

        # Draw throat outline (hourglass shape)
        for i in range(height - 4):
            t = (i / (height - 4)) * 2 - 1  # -1 to 1
            throat_radius = int((1 + t*t) * (width // 8))
            current_row = row + 2 + i

            if row < current_row < row + height:
                if col < center_col - throat_radius < col + width:
                    buffer.write(current_row, center_col - throat_radius, "(")
                if col < center_col + throat_radius < col + width:
                    buffer.write(current_row, center_col + throat_radius, ")")

        # Plot points
        for point in points:
            x, y = point.get("x", 0.0), point.get("y", 0.0)
            screen_row = center_row + int(y * (height // 4))
            screen_col = center_col + int(x * (width // 4))

            if row < screen_row < row + height and col < screen_col < col + width:
                marker = self._get_curvature_marker(curvature, capabilities)
                buffer.write(screen_row, screen_col, marker)

    def _render_fiber_bundle(self, buffer, position, points, curvature, capabilities):
        """Render fiber bundle projection."""
        row, col, height, width = position.row, position.col, position.height, position.width

        # Draw fiber lines
        for i in range(0, width - 4, 8):
            for j in range(height - 4):
                current_row = row + 2 + j
                current_col = col + 2 + i

                if row < current_row < row + height and col < current_col < col + width:
                    buffer.write(current_row, current_col, "|" if j % 2 == 0 else ":")

        # Plot points
        center_row = row + height // 2
        center_col = col + width // 2

        for point in points:
            x, y = point.get("x", 0.0), point.get("y", 0.0)
            screen_row = center_row + int(y * (height // 4))
            screen_col = center_col + int(x * (width // 4))

            if row < screen_row < row + height and col < screen_col < col + width:
                marker = self._get_curvature_marker(curvature, capabilities)
                buffer.write(screen_row, screen_col, marker)

    def _render_klein_disk(self, buffer, position, points, curvature, capabilities):
        """Render Klein disk model."""
        # Similar to Poincaré but with different metric
        self._render_poincare_disk(buffer, position, points, curvature, capabilities)

    def _render_upper_half_plane(self, buffer, position, points, curvature, capabilities):
        """Render upper half-plane model."""
        row, col, height, width = position.row, position.col, position.height, position.width

        # Draw horizon line
        horizon_row = row + height - 3
        for c in range(col, col + width):
            buffer.write(horizon_row, c, "─" if capabilities.get("unicode_support") else "-")

        # Plot points (only upper half)
        for point in points:
            x, y = point.get("x", 0.0), point.get("y", 0.0)
            if y > 0:  # Upper half only
                screen_row = horizon_row - int(y * (height // 2))
                screen_col = col + width // 2 + int(x * (width // 4))

                if row < screen_row < row + height and col < screen_col < col + width:
                    marker = self._get_curvature_marker(curvature, capabilities)
                    buffer.write(screen_row, screen_col, marker)

    def _render_beltrami_klein(self, buffer, position, points, curvature, capabilities):
        """Render Beltrami-Klein model."""
        self._render_klein_disk(buffer, position, points, curvature, capabilities)

    def _render_hemisphere(self, buffer, position, points, curvature, capabilities):
        """Render hemisphere projection."""
        row, col, height, width = position.row, position.col, position.height, position.width
        center_row = row + height - 3
        center_col = col + width // 2
        radius = min(height - 4, width // 4)

        # Draw hemisphere arc
        for angle in range(0, 181, 10):
            rad = math.radians(angle)
            r = center_row - int(radius * math.sin(rad))
            c = center_col + int(radius * 2 * math.cos(rad))

            if row < r < row + height and col < c < col + width:
                buffer.write(r, c, "·" if capabilities.get("unicode_support") else ".")

        # Plot points
        for point in points:
            x, y = point.get("x", 0.0), point.get("y", 0.0)
            screen_row = center_row - int(abs(y) * radius)
            screen_col = center_col + int(x * radius * 2)

            if row < screen_row < row + height and col < screen_col < col + width:
                marker = self._get_curvature_marker(curvature, capabilities)
                buffer.write(screen_row, screen_col, marker)

    def _render_lorentz(self, buffer, position, points, curvature, capabilities):
        """Render Lorentz (Minkowski) spacetime diagram."""
        row, col, height, width = position.row, position.col, position.height, position.width
        center_row = row + height // 2
        center_col = col + width // 2

        # Draw light cones
        for i in range(height // 2):
            offset = i

            # Future light cone
            if row < center_row - i < row + height:
                if col < center_col - offset < col + width:
                    buffer.write(center_row - i, center_col - offset, "/")
                if col < center_col + offset < col + width:
                    buffer.write(center_row - i, center_col + offset, "\\")

            # Past light cone
            if row < center_row + i < row + height:
                if col < center_col - offset < col + width:
                    buffer.write(center_row + i, center_col - offset, "\\")
                if col < center_col + offset < col + width:
                    buffer.write(center_row + i, center_col + offset, "/")

        # Plot points
        for point in points:
            x, t = point.get("x", 0.0), point.get("t", 0.0)
            screen_row = center_row - int(t * (height // 4))
            screen_col = center_col + int(x * (width // 4))

            if row < screen_row < row + height and col < screen_col < col + width:
                marker = self._get_curvature_marker(curvature, capabilities)
                buffer.write(screen_row, screen_col, marker)

    def _get_curvature_marker(self, curvature: str, capabilities: Dict[str, Any]) -> str:
        """Get marker based on curvature domain."""
        if not capabilities.get("unicode_support"):
            return "*"

        markers = {
            "positive": "◉",  # Spherical
            "zero": "○",      # Flat
            "negative": "●",  # Hyperbolic
            "mixed": "◐"      # Transition
        }

        return markers.get(curvature, "●")


def create_hyperbolic_renderer() -> HyperbolicSliceRenderer:
    """Create hyperbolic slice renderer."""
    return HyperbolicSliceRenderer()
