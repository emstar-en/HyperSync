"""
Curvature Field Renderer

Visualizes curvature fields with scalar, Gaussian, and Ricci flow.
"""

import logging
from typing import Dict, Any


logger = logging.getLogger(__name__)


class CurvatureFieldRenderer:
    """
    Curvature field renderer.

    Visualizes:
    - Scalar curvature
    - Gaussian curvature
    - Ricci flow
    - Sectional curvature
    """

    def __init__(self):
        logger.info("CurvatureFieldRenderer initialized")

    def render(
        self,
        buffer: Any,
        position: Any,
        field_data: Dict[str, float],
        capabilities: Dict[str, Any]
    ):
        """
        Render curvature field.

        Args:
            buffer: Render buffer
            position: Panel position
            field_data: Curvature field data
            capabilities: Terminal capabilities
        """
        row = position.row
        col = position.col
        height = position.height
        width = position.width

        # Title
        title = "┌─ Curvature Field ─┐" if capabilities.get("unicode_support") else "+- Curvature Field -+"
        buffer.write(row, col, title[:width])

        current_row = row + 1

        # Scalar curvature
        scalar = field_data.get("scalar_curvature", 0.0)
        bar = self._render_bar(scalar, width - 20, capabilities)
        line = f"Scalar:   {scalar:5.2f} {bar}"
        buffer.write(current_row, col, line[:width])
        current_row += 1

        # Gaussian curvature
        gaussian = field_data.get("gaussian_curvature", 0.0)
        bar = self._render_bar(gaussian, width - 20, capabilities)
        line = f"Gaussian: {gaussian:5.2f} {bar}"
        buffer.write(current_row, col, line[:width])
        current_row += 1

        # Ricci flow
        ricci = field_data.get("ricci_flow", 0.0)
        bar = self._render_bar(ricci, width - 20, capabilities)
        line = f"Ricci:    {ricci:5.2f} {bar}"
        buffer.write(current_row, col, line[:width])
        current_row += 1

        # Sectional curvature (if available)
        if "sectional_curvature" in field_data:
            sectional = field_data["sectional_curvature"]
            bar = self._render_bar(sectional, width - 20, capabilities)
            line = f"Sectional:{sectional:5.2f} {bar}"
            buffer.write(current_row, col, line[:width])
            current_row += 1

        # Footer
        footer = "└" + "─" * (width - 2) + "┘" if capabilities.get("unicode_support") else "+" + "-" * (width - 2) + "+"
        if current_row < row + height:
            buffer.write(current_row, col, footer[:width])

    def _render_bar(self, value: float, width: int, capabilities: Dict[str, Any]) -> str:
        """Render progress bar."""
        filled = int(value * width)

        if capabilities.get("unicode_support"):
            return "█" * filled + "░" * (width - filled)
        else:
            return "#" * filled + "-" * (width - filled)


def create_curvature_renderer() -> CurvatureFieldRenderer:
    """Create curvature field renderer."""
    return CurvatureFieldRenderer()
