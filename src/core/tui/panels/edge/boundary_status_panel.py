"""
Boundary Status Panel

Displays edge/boundary telemetry and status.
"""

import logging
from typing import Dict, Any


logger = logging.getLogger(__name__)


def render_boundary_status_panel(
    buffer: Any,
    position: Any,
    config: Dict[str, Any],
    state: Dict[str, Any],
    capabilities: Dict[str, Any]
):
    """
    Render boundary status panel.

    Displays:
    - Boundary gate status
    - Throughput metrics
    - Edge connectivity

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

    # Get boundary data
    boundaries = state.get("boundaries", [])

    # Render title
    title = "┌─ Boundary Status ─┐" if capabilities.get("unicode_support") else "+- Boundary Status -+"
    buffer.write(row, col, title[:width])

    # Render boundary list
    current_row = row + 1

    for i, boundary in enumerate(boundaries[:height - 2]):
        if current_row >= row + height - 1:
            break

        boundary_id = boundary.get("id", "unknown")[:12]
        status = boundary.get("status", "unknown")
        throughput = boundary.get("throughput", 0.0)

        # Status indicator
        if status == "active":
            indicator = "●" if capabilities.get("unicode_support") else "*"
        elif status == "degraded":
            indicator = "◐" if capabilities.get("unicode_support") else "o"
        else:
            indicator = "○" if capabilities.get("unicode_support") else "."

        line = f"{indicator} {boundary_id:12s} {throughput:6.1f} MB/s"
        buffer.write(current_row, col, line[:width])

        current_row += 1

    # Render footer
    footer = "└" + "─" * (width - 2) + "┘" if capabilities.get("unicode_support") else "+" + "-" * (width - 2) + "+"
    if current_row < row + height:
        buffer.write(current_row, col, footer[:width])


def register_boundary_status_panel(registry):
    """Register boundary status panel with registry."""
    from hypersync.tui.panels.registry import PanelMetadata, PanelCategory

    metadata = PanelMetadata(
        id="boundary_status",
        type="boundary_status",
        title="Boundary Status",
        description="Edge and boundary telemetry with throughput metrics",
        category=PanelCategory.MONITORING,
        min_tier="SMALL",
        requires_unicode=False,
        requires_color=False
    )

    registry.register("boundary_status", metadata, render_boundary_status_panel)
