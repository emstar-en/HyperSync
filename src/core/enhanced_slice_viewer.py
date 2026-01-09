"""
Enhanced Slice Viewer Panel - Uses hyperbolic renderer instead of ASCII.

This replaces the primitive ASCII rendering with proper hyperbolic geometry
visualization using the HyperbolicSliceRenderer.
"""
import logging
from typing import Dict, Any, List, Optional
import numpy as np

from hypersync.tui.renderers.renderer_registry import (
    get_renderer_registry,
    RendererType,
    RenderMode
)
from hypersync.tui.renderers.renderer_config import get_config_manager
from hypersync.tui.panels.state_handlers import get_panel_state

logger = logging.getLogger(__name__)


class EnhancedSliceViewerPanel:
    """
    Enhanced slice viewer panel with hyperbolic rendering.

    Displays a slice of hyperbolic space with anchors, geodesics,
    and curvature visualization.
    """

    def __init__(self, panel_id: str = "hyperbolic_slice"):
        self.panel_id = panel_id
        self.renderer_registry = get_renderer_registry()
        self.config_manager = get_config_manager()
        self.current_mode = RenderMode.FILLED
        self.current_slice_depth = 0.0
        self._renderer = None

    def _get_renderer(self):
        """Get or create the hyperbolic slice renderer."""
        if self._renderer is None:
            self._renderer = self.renderer_registry.get_renderer(
                RendererType.HYPERBOLIC_SLICE,
                mode=self.current_mode
            )
        return self._renderer

    def render(self, width: int, height: int) -> str:
        """
        Render the hyperbolic slice panel.

        Args:
            width: Panel width in characters
            height: Panel height in characters

        Returns:
            Rendered panel as string
        """
        renderer = self._get_renderer()

        if renderer is None:
            return self._render_fallback(width, height)

        # Get current state
        anchor_state = get_panel_state("anchor")
        geodesic_state = get_panel_state("geodesic")
        curvature_state = get_panel_state("curvature")

        # Extract data
        anchors = anchor_state.get("anchors", [])
        paths = geodesic_state.get("paths", [])
        curvature_map = curvature_state.get("curvature_map", {})

        # Convert to renderer format
        points = self._extract_points(anchors, self.current_slice_depth)
        geodesics = self._extract_geodesics(paths, self.current_slice_depth)
        curvature_field = self._extract_curvature_field(curvature_map)

        # Get config
        config = self.config_manager.get_config(self.panel_id)

        # Update config with current dimensions
        config.width = width
        config.height = height

        try:
            # Render using hyperbolic renderer
            output = renderer.render(
                points=points,
                geodesics=geodesics,
                curvature_field=curvature_field,
                slice_depth=self.current_slice_depth,
                config=config
            )

            # Add header and footer
            header = self._render_header(width)
            footer = self._render_footer(width, anchor_state, geodesic_state)

            return f"{header}\n{output}\n{footer}"

        except Exception as e:
            logger.error(f"Rendering error: {e}", exc_info=True)
            return self._render_fallback(width, height)

    def _extract_points(self, anchors: List[Dict], slice_depth: float) -> np.ndarray:
        """Extract anchor points for rendering."""
        points = []
        for anchor in anchors:
            pos = anchor.get("position", [0, 0, 0])
            # Filter by slice depth (only show points near this depth)
            if len(pos) >= 3 and abs(pos[2] - slice_depth) < 0.1:
                points.append([pos[0], pos[1]])

        return np.array(points) if points else np.array([]).reshape(0, 2)

    def _extract_geodesics(self, paths: List[Dict], slice_depth: float) -> List[np.ndarray]:
        """Extract geodesic paths for rendering."""
        geodesics = []
        for path in paths:
            points = path.get("points", [])
            # Filter points by slice depth
            filtered = [
                [p[0], p[1]] for p in points
                if len(p) >= 3 and abs(p[2] - slice_depth) < 0.1
            ]
            if len(filtered) >= 2:
                geodesics.append(np.array(filtered))

        return geodesics

    def _extract_curvature_field(self, curvature_map: Dict) -> Optional[np.ndarray]:
        """Extract curvature field for rendering."""
        if not curvature_map:
            return None

        # Convert curvature map to 2D array
        # This is a simplified version - real implementation would be more sophisticated
        try:
            values = list(curvature_map.values())
            if values:
                # Create a simple grid
                size = int(np.sqrt(len(values)))
                if size * size == len(values):
                    return np.array(values).reshape(size, size)
        except Exception as e:
            logger.warning(f"Could not extract curvature field: {e}")

        return None

    def _render_header(self, width: int) -> str:
        """Render panel header."""
        title = f" Hyperbolic Slice (depth: {self.current_slice_depth:.2f}) "
        mode_str = f" [{self.current_mode.value}] "

        # Center title
        padding = (width - len(title) - len(mode_str)) // 2
        header = "─" * padding + title + "─" * (width - padding - len(title) - len(mode_str)) + mode_str

        return header[:width]

    def _render_footer(
        self,
        width: int,
        anchor_state: Dict,
        geodesic_state: Dict
    ) -> str:
        """Render panel footer with stats."""
        anchor_count = anchor_state.get("total_count", 0)
        geodesic_count = geodesic_state.get("active_routes", 0)

        stats = f" Anchors: {anchor_count} | Geodesics: {geodesic_count} "
        footer = "─" * ((width - len(stats)) // 2) + stats
        footer += "─" * (width - len(footer))

        return footer[:width]

    def _render_fallback(self, width: int, height: int) -> str:
        """Fallback ASCII rendering when renderer unavailable."""
        lines = []
        lines.append("─" * width)
        lines.append(" Hyperbolic Slice Viewer (ASCII Fallback)".ljust(width))
        lines.append("─" * width)

        # Get state
        anchor_state = get_panel_state("anchor")
        anchors = anchor_state.get("anchors", [])

        # Simple ASCII visualization
        for i in range(height - 5):
            line = " " * width
            lines.append(line)

        # Footer
        lines.append("─" * width)
        lines.append(f" Anchors: {len(anchors)} ".ljust(width))

        return "\n".join(lines[:height])

    def set_mode(self, mode: RenderMode) -> None:
        """Change rendering mode."""
        self.current_mode = mode
        self._renderer = None  # Force recreation with new mode

    def set_slice_depth(self, depth: float) -> None:
        """Change slice depth."""
        self.current_slice_depth = depth

    def cycle_mode(self) -> None:
        """Cycle through rendering modes."""
        modes = [RenderMode.WIREFRAME, RenderMode.FILLED, RenderMode.GRADIENT]
        current_idx = modes.index(self.current_mode)
        next_idx = (current_idx + 1) % len(modes)
        self.set_mode(modes[next_idx])
