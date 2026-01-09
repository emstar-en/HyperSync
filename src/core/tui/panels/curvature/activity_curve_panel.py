"""
Curvature Activity Panel

Displays geodesic activity curves and curvature metrics.
"""

import logging
from typing import Dict, Any


logger = logging.getLogger(__name__)


def render_activity_curve_panel(
    buffer: Any,
    position: Any,
    config: Dict[str, Any],
    state: Dict[str, Any],
    capabilities: Dict[str, Any]
):
    """
    Render curvature activity curve panel.

    Displays:
    - Time-series geodesic activity
    - Curvature metrics
    - Agent annotations
    - Threshold markers

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

    # Get activity data
    activity = state.get("activity", [])
    max_value = max(activity) if activity else 1.0

    # Render title
    title = "┌─ Geodesic Activity ─┐" if capabilities.get("unicode_support") else "+- Geodesic Activity -+"
    buffer.write(row, col, title[:width])

    # Render time series
    chart_height = height - 3
    chart_width = width - 4

    if capabilities.get("unicode_support"):
        # Use Braille characters for smooth curves
        braille_base = 0x2800

        for i in range(min(len(activity), chart_width)):
            value = activity[i]
            normalized = int((value / max_value) * chart_height * 4)

            chart_row = row + 1 + (chart_height - 1 - (normalized // 4))
            chart_col = col + 2 + i

            if 0 <= chart_row < row + height - 1:
                # Simple block for now
                buffer.write(chart_row, chart_col, "█")
    else:
        # ASCII fallback
        for i in range(min(len(activity), chart_width)):
            value = activity[i]
            normalized = int((value / max_value) * chart_height)

            chart_row = row + 1 + (chart_height - 1 - normalized)
            chart_col = col + 2 + i

            if 0 <= chart_row < row + height - 1:
                buffer.write(chart_row, chart_col, "#")

    # Render footer with stats
    if activity:
        avg = sum(activity) / len(activity)
        footer = f"Avg: {avg:.2f} Max: {max_value:.2f}"
    else:
        footer = "No data"

    if row + height - 1 < row + height:
        buffer.write(row + height - 1, col, footer[:width])


def register_activity_curve_panel(registry):
    """Register activity curve panel with registry."""
    from hypersync.tui.panels.registry import PanelMetadata, PanelCategory

    metadata = PanelMetadata(
        id="activity_curve",
        type="activity_curve",
        title="Geodesic Activity",
        description="Time-series geodesic activity curves with curvature metrics",
        category=PanelCategory.MONITORING,
        min_tier="STANDARD",
        requires_unicode=False,
        requires_color=False
    )

    registry.register("activity_curve", metadata, render_activity_curve_panel)
