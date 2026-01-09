"""
Live Anchor Panel

Displays real-time anchor readings, resonance, intensity, and anomalies.
"""

import logging
from typing import Dict, Any


logger = logging.getLogger(__name__)


def render_anchor_panel(
    buffer: Any,
    position: Any,
    config: Dict[str, Any],
    state: Dict[str, Any],
    capabilities: Dict[str, Any]
):
    """
    Render live anchor panel.

    Displays:
    - Anchor resonance/intensity per anchor
    - Trust bands
    - Anomaly flags
    - Real-time updates

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

    # Get anchor data from state
    anchors = state.get("anchors", [])

    # Render title
    title = "┌─ Live Anchors ─┐" if capabilities.get("unicode_support") else "+- Live Anchors -+"
    buffer.write(row, col, title[:width])

    # Render anchor list
    current_row = row + 1

    for i, anchor in enumerate(anchors[:height - 2]):
        if current_row >= row + height - 1:
            break

        # Format anchor info
        anchor_id = anchor.get("id", "unknown")[:10]
        resonance = anchor.get("resonance", 0.0)
        intensity = anchor.get("intensity", 0.0)
        anomaly = anchor.get("anomaly", False)

        # Create bar for resonance
        bar_width = int((width - 25) * resonance)
        bar = "█" * bar_width if capabilities.get("unicode_support") else "#" * bar_width

        # Anomaly indicator
        indicator = "⚠" if anomaly and capabilities.get("unicode_support") else "!" if anomaly else " "

        # Format line
        line = f"{indicator} {anchor_id:10s} {resonance:5.2f} {bar}"
        buffer.write(current_row, col, line[:width])

        current_row += 1

    # Render footer
    footer = "└" + "─" * (width - 2) + "┘" if capabilities.get("unicode_support") else "+" + "-" * (width - 2) + "+"
    if current_row < row + height:
        buffer.write(current_row, col, footer[:width])


def register_anchor_panel(registry):
    """Register anchor panel with registry."""
    from hypersync.tui.panels.registry import PanelMetadata, PanelCategory

    metadata = PanelMetadata(
        id="live_anchor",
        type="live_anchor",
        title="Live Anchors",
        description="Real-time anchor readings with resonance and anomaly detection",
        category=PanelCategory.MONITORING,
        min_tier="SMALL",
        requires_unicode=False,
        requires_color=False
    )

    registry.register("live_anchor", metadata, render_anchor_panel)
