"""
TUI Server Bootstrap - Enhanced initialization with adapter wiring.

Handles the complete startup sequence for the TUI server including
data adapter registration and lifecycle management.
"""
import asyncio
import logging
import os
from typing import Optional

from hypersync.tui.data_bridge import get_registry
from hypersync.tui.panels.state_handlers import (
    anchor_state_handler,
    geodesic_state_handler,
    curvature_state_handler,
    boundary_state_handler,
    metrics_state_handler
)

logger = logging.getLogger(__name__)


class TUIBootstrap:
    """Manages TUI server bootstrap and shutdown."""

    def __init__(self):
        self.registry = get_registry()
        self._initialized = False

    async def initialize(self) -> None:
        """
        Initialize the TUI server with all adapters and handlers.

        This is the main entry point for wiring up the data flow.
        """
        if self._initialized:
            logger.warning("TUI already initialized")
            return

        logger.info("Initializing TUI server...")

        # Import adapters (lazy import to avoid circular dependencies)
        from hypersync.tui.data_sources.anchor_adapter import AnchorAdapter
        from hypersync.tui.data_sources.geodesic_adapter import GeodesicAdapter
        from hypersync.tui.data_sources.curvature_adapter import CurvatureAdapter

        # Get poll intervals from environment or use defaults
        anchor_interval = float(os.getenv("HYPERSYNC_ANCHOR_POLL_INTERVAL", "1.0"))
        geodesic_interval = float(os.getenv("HYPERSYNC_GEODESIC_POLL_INTERVAL", "0.5"))
        curvature_interval = float(os.getenv("HYPERSYNC_CURVATURE_POLL_INTERVAL", "2.0"))

        # Register adapters
        logger.info("Registering data adapters...")
        self.registry.register_adapter(
            "anchor",
            AnchorAdapter(),
            poll_interval=anchor_interval
        )
        self.registry.register_adapter(
            "geodesic",
            GeodesicAdapter(),
            poll_interval=geodesic_interval
        )
        self.registry.register_adapter(
            "curvature",
            CurvatureAdapter(),
            poll_interval=curvature_interval
        )

        # Subscribe state handlers to adapters
        logger.info("Wiring state handlers...")
        self.registry.subscribe("anchor", anchor_state_handler)
        self.registry.subscribe("geodesic", geodesic_state_handler)
        self.registry.subscribe("curvature", curvature_state_handler)

        # Boundary and metrics handlers listen to multiple sources
        self.registry.subscribe("anchor", boundary_state_handler)
        self.registry.subscribe("geodesic", boundary_state_handler)
        self.registry.subscribe("curvature", metrics_state_handler)
        self.registry.subscribe("geodesic", metrics_state_handler)

        # Start all adapters
        logger.info("Starting data adapters...")
        await self.registry.start_all()

        self._initialized = True
        logger.info("TUI server initialized successfully")

    async def shutdown(self) -> None:
        """Gracefully shutdown the TUI server."""
        if not self._initialized:
            return

        logger.info("Shutting down TUI server...")
        await self.registry.stop_all()
        self._initialized = False
        logger.info("TUI server shutdown complete")

    def get_status(self) -> dict:
        """Get current status of the TUI server."""
        return {
            "initialized": self._initialized,
            "adapters": self.registry.get_status()
        }


# Global bootstrap instance
_bootstrap: Optional[TUIBootstrap] = None


def get_bootstrap() -> TUIBootstrap:
    """Get the global TUI bootstrap instance."""
    global _bootstrap
    if _bootstrap is None:
        _bootstrap = TUIBootstrap()
    return _bootstrap
