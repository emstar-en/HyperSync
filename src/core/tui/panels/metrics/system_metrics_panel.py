"""
System Metrics Panel

Displays system metrics enhanced with hyperdimensional telemetry.
"""

import logging
from typing import Dict, Any


logger = logging.getLogger(__name__)


def render_system_metrics_panel(
    buffer: Any,
    position: Any,
    config: Dict[str, Any],
    state: Dict[str, Any],
    capabilities: Dict[str, Any]
):
    """
    Render system metrics panel.

    Displays:
    - CPU, memory, disk usage
    - Network I/O
    - Hyperdimensional metrics

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

    # Get metrics
    metrics = state.get("metrics", {})

    # Render title
    title = "┌─ System Metrics ─┐" if capabilities.get("unicode_support") else "+- System Metrics -+"
    buffer.write(row, col, title[:width])

    current_row = row + 1

    # CPU
    cpu = metrics.get("cpu_percent", 0.0)
    cpu_bar = _render_bar(cpu / 100.0, width - 15, capabilities)
    line = f"CPU:  {cpu:5.1f}% {cpu_bar}"
    buffer.write(current_row, col, line[:width])
    current_row += 1

    # Memory
    memory = metrics.get("memory_percent", 0.0)
    memory_bar = _render_bar(memory / 100.0, width - 15, capabilities)
    line = f"Mem:  {memory:5.1f}% {memory_bar}"
    buffer.write(current_row, col, line[:width])
    current_row += 1

    # Disk
    disk = metrics.get("disk_percent", 0.0)
    disk_bar = _render_bar(disk / 100.0, width - 15, capabilities)
    line = f"Disk: {disk:5.1f}% {disk_bar}"
    buffer.write(current_row, col, line[:width])
    current_row += 1

    # Network
    net_in = metrics.get("net_in_mbps", 0.0)
    net_out = metrics.get("net_out_mbps", 0.0)
    line = f"Net:  ↓{net_in:6.1f} ↑{net_out:6.1f} MB/s"
    buffer.write(current_row, col, line[:width])
    current_row += 1

    # Hyperdimensional metrics
    if current_row < row + height - 1:
        buffer.write(current_row, col, "─" * width if capabilities.get("unicode_support") else "-" * width)
        current_row += 1

    # Curvature stress
    curvature = metrics.get("curvature_stress", 0.0)
    line = f"Curv: {curvature:5.2f}"
    if current_row < row + height - 1:
        buffer.write(current_row, col, line[:width])
        current_row += 1

    # Geodesic load
    geodesic = metrics.get("geodesic_load", 0.0)
    line = f"Geo:  {geodesic:5.2f}"
    if current_row < row + height - 1:
        buffer.write(current_row, col, line[:width])
        current_row += 1

    # Render footer
    footer = "└" + "─" * (width - 2) + "┘" if capabilities.get("unicode_support") else "+" + "-" * (width - 2) + "+"
    if current_row < row + height:
        buffer.write(current_row, col, footer[:width])


def _render_bar(value: float, width: int, capabilities: Dict[str, Any]) -> str:
    """Render progress bar."""
    filled = int(value * width)

    if capabilities.get("unicode_support"):
        return "█" * filled + "░" * (width - filled)
    else:
        return "#" * filled + "-" * (width - filled)


def register_system_metrics_panel(registry):
    """Register system metrics panel with registry."""
    from hypersync.tui.panels.registry import PanelMetadata, PanelCategory

    metadata = PanelMetadata(
        id="system_metrics",
        type="system_metrics",
        title="System Metrics",
        description="System metrics enhanced with hyperdimensional telemetry",
        category=PanelCategory.MONITORING,
        min_tier="MICRO",
        requires_unicode=False,
        requires_color=False
    )

    registry.register("system_metrics", metadata, render_system_metrics_panel)
