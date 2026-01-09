"""
Hyperbolic Slice Viewer Panel

Displays hyperbolic space slices with multiple geometry modes.
Initial support for Poincaré disk, hyperboloid, and black-hole lens.
Full geometry support added in Patch 055.
"""

import logging
import math
from typing import Dict, Any


logger = logging.getLogger(__name__)


def render_slice_viewer_panel(
    buffer: Any,
    position: Any,
    config: Dict[str, Any],
    state: Dict[str, Any],
    capabilities: Dict[str, Any]
):
    """
    Render hyperbolic slice viewer panel.

    Initial modes:
    - Poincaré disk
    - Hyperboloid
    - Black-hole lens

    Full geometry support in Patch 055.

    Args:
        buffer: Render buffer
        position: Panel position
        config: Panel configuration
        state: Panel state
        capabilities: Terminal capabilities
    """
    row = position.row
    col = position.col
    height = position.height
    width = position.width

    # Get geometry mode
    mode = config.get("geometry_mode", "poincare_disk")

    # Render title
    title = f"┌─ Hyperbolic Slice ({mode}) ─┐" if capabilities.get("unicode_support") else f"+- Hyperbolic Slice ({mode}) -+"
    buffer.write(row, col, title[:width])

    # Get slice data
    points = state.get("points", [])

    # Render based on mode
    if mode == "poincare_disk":
        _render_poincare_disk(buffer, row, col, height, width, points, capabilities)
    elif mode == "hyperboloid":
        _render_hyperboloid(buffer, row, col, height, width, points, capabilities)
    elif mode == "black_hole_lens":
        _render_black_hole_lens(buffer, row, col, height, width, points, capabilities)
    else:
        # Placeholder for other modes (Patch 055)
        buffer.write(row + height // 2, col + 2, f"Mode '{mode}' coming in Patch 055")

    # Render footer
    footer = f"Points: {len(points)}"
    if row + height - 1 < row + height:
        buffer.write(row + height - 1, col, footer[:width])


def _render_poincare_disk(buffer, row, col, height, width, points, capabilities):
    """Render Poincaré disk projection."""
    # Calculate center and radius
    center_row = row + height // 2
    center_col = col + width // 2
    radius = min(height // 2 - 2, width // 4 - 2)

    # Draw circle boundary
    if capabilities.get("unicode_support"):
        for angle in range(0, 360, 10):
            rad = math.radians(angle)
            r = center_row + int(radius * math.sin(rad))
            c = center_col + int(radius * 2 * math.cos(rad))

            if row < r < row + height and col < c < col + width:
                buffer.write(r, c, "·")
    else:
        # ASCII circle
        for angle in range(0, 360, 15):
            rad = math.radians(angle)
            r = center_row + int(radius * math.sin(rad))
            c = center_col + int(radius * 2 * math.cos(rad))

            if row < r < row + height and col < c < col + width:
                buffer.write(r, c, ".")

    # Plot points
    for point in points:
        x = point.get("x", 0.0)
        y = point.get("y", 0.0)

        # Map to screen coordinates
        screen_row = center_row + int(y * radius)
        screen_col = center_col + int(x * radius * 2)

        if row < screen_row < row + height and col < screen_col < col + width:
            marker = "●" if capabilities.get("unicode_support") else "*"
            buffer.write(screen_row, screen_col, marker)


def _render_hyperboloid(buffer, row, col, height, width, points, capabilities):
    """Render hyperboloid projection."""
    # Simplified hyperboloid rendering
    center_row = row + height // 2
    center_col = col + width // 2

    # Draw hyperboloid outline
    for i in range(height - 4):
        offset = int(math.sqrt(i) * 2)

        left_col = center_col - offset
        right_col = center_col + offset
        current_row = row + 2 + i

        if row < current_row < row + height:
            if col < left_col < col + width:
                buffer.write(current_row, left_col, "|")
            if col < right_col < col + width:
                buffer.write(current_row, right_col, "|")

    # Plot points
    for point in points:
        x = point.get("x", 0.0)
        y = point.get("y", 0.0)
        z = point.get("z", 0.0)

        # Project to 2D
        screen_row = center_row + int(z * (height // 4))
        screen_col = center_col + int(x * (width // 4))

        if row < screen_row < row + height and col < screen_col < col + width:
            marker = "●" if capabilities.get("unicode_support") else "*"
            buffer.write(screen_row, screen_col, marker)


def _render_black_hole_lens(buffer, row, col, height, width, points, capabilities):
    """Render black-hole lens projection."""
    # Penrose diagram style
    center_row = row + height // 2
    center_col = col + width // 2

    # Draw light cone boundaries
    for i in range(height - 4):
        offset = i

        left_col = center_col - offset
        right_col = center_col + offset
        current_row = row + 2 + i

        if row < current_row < row + height:
            if col < left_col < col + width:
                buffer.write(current_row, left_col, "/")
            if col < right_col < col + width:
                buffer.write(current_row, right_col, "\\")

    # Plot points with lensing effect
    for point in points:
        x = point.get("x", 0.0)
        y = point.get("y", 0.0)

        # Apply lensing distortion
        r = math.sqrt(x*x + y*y)
        if r > 0:
            lens_factor = 1.0 / (1.0 + r)
            x *= lens_factor
            y *= lens_factor

        screen_row = center_row + int(y * (height // 4))
        screen_col = center_col + int(x * (width // 4))

        if row < screen_row < row + height and col < screen_col < col + width:
            marker = "●" if capabilities.get("unicode_support") else "*"
            buffer.write(screen_row, screen_col, marker)


def register_slice_viewer_panel(registry):
    """Register hyperbolic slice viewer panel with registry."""
    from hypersync.tui.panels.registry import PanelMetadata, PanelCategory

    metadata = PanelMetadata(
        id="hyperbolic_slice",
        type="hyperbolic_slice",
        title="Hyperbolic Slice Viewer",
        description="Multi-mode hyperbolic space visualization (Poincaré, hyperboloid, black-hole lens)",
        category=PanelCategory.VISUALIZATION,
        min_tier="STANDARD",
        requires_unicode=False,
        requires_color=False
    )

    registry.register("hyperbolic_slice", metadata, render_slice_viewer_panel)
