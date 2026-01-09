"""
HyperSync TUI Panel Registry

Panel metadata, render callbacks, and lifecycle management.
"""

import logging
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass
from enum import Enum, auto


logger = logging.getLogger(__name__)


class PanelCategory(Enum):
    """Panel categories."""
    MONITORING = auto()
    CONTROL = auto()
    VISUALIZATION = auto()
    SYSTEM = auto()
    CUSTOM = auto()


@dataclass
class PanelMetadata:
    """Panel metadata."""
    id: str
    type: str
    title: str
    description: str
    category: PanelCategory
    min_tier: str  # Minimum terminal tier required
    requires_unicode: bool = False
    requires_color: bool = False
    requires_mouse: bool = False


class PanelRegistry:
    """
    Panel registry.

    Manages panel types, metadata, and render callbacks.
    """

    def __init__(self):
        self.panels: Dict[str, PanelMetadata] = {}
        self.renderers: Dict[str, Callable] = {}
        self.instances: Dict[str, Any] = {}
        logger.info("PanelRegistry initialized")

    def register(
        self,
        panel_type: str,
        metadata: PanelMetadata,
        renderer: Callable
    ):
        """
        Register panel type.

        Args:
            panel_type: Panel type identifier
            metadata: Panel metadata
            renderer: Render callback function
        """
        self.panels[panel_type] = metadata
        self.renderers[panel_type] = renderer

        logger.info(f"Registered panel type: {panel_type}")

    def unregister(self, panel_type: str):
        """Unregister panel type."""
        if panel_type in self.panels:
            del self.panels[panel_type]
            del self.renderers[panel_type]
            logger.info(f"Unregistered panel type: {panel_type}")

    def get_metadata(self, panel_type: str) -> Optional[PanelMetadata]:
        """Get panel metadata."""
        return self.panels.get(panel_type)

    def get_renderer(self, panel_type: str) -> Optional[Callable]:
        """Get panel renderer."""
        return self.renderers.get(panel_type)

    def list_panels(
        self,
        category: Optional[PanelCategory] = None,
        min_tier: Optional[str] = None
    ) -> List[PanelMetadata]:
        """
        List registered panels.

        Args:
            category: Filter by category
            min_tier: Filter by minimum tier

        Returns:
            List of panel metadata
        """
        panels = list(self.panels.values())

        if category:
            panels = [p for p in panels if p.category == category]

        if min_tier:
            # TODO: Implement tier filtering
            pass

        return panels

    def create_instance(self, panel_id: str, panel_type: str, config: Dict[str, Any]) -> bool:
        """
        Create panel instance.

        Args:
            panel_id: Unique panel instance ID
            panel_type: Panel type
            config: Panel configuration

        Returns:
            True if instance was created
        """
        if panel_type not in self.panels:
            logger.warning(f"Unknown panel type: {panel_type}")
            return False

        if panel_id in self.instances:
            logger.warning(f"Panel instance already exists: {panel_id}")
            return False

        # Create instance
        self.instances[panel_id] = {
            "type": panel_type,
            "config": config,
            "state": {}
        }

        logger.debug(f"Created panel instance: {panel_id} ({panel_type})")

        return True

    def destroy_instance(self, panel_id: str) -> bool:
        """Destroy panel instance."""
        if panel_id in self.instances:
            del self.instances[panel_id]
            logger.debug(f"Destroyed panel instance: {panel_id}")
            return True

        return False

    def get_instance(self, panel_id: str) -> Optional[Dict[str, Any]]:
        """Get panel instance."""
        return self.instances.get(panel_id)

    def render_panel(
        self,
        panel_id: str,
        buffer: Any,
        position: Any,
        capabilities: Dict[str, Any]
    ) -> bool:
        """
        Render panel to buffer.

        Args:
            panel_id: Panel instance ID
            buffer: Render buffer
            position: Panel position
            capabilities: Terminal capabilities

        Returns:
            True if panel was rendered
        """
        instance = self.instances.get(panel_id)
        if not instance:
            return False

        panel_type = instance["type"]
        renderer = self.renderers.get(panel_type)

        if not renderer:
            return False

        try:
            renderer(buffer, position, instance["config"], instance["state"], capabilities)
            return True
        except Exception as e:
            logger.error(f"Error rendering panel {panel_id}: {e}")
            return False


# Global panel registry
_panel_registry = None


def get_panel_registry() -> PanelRegistry:
    """Get global panel registry."""
    global _panel_registry
    if _panel_registry is None:
        _panel_registry = PanelRegistry()
    return _panel_registry
