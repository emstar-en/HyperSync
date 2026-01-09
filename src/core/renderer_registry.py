"""
Renderer Registry - Central management for TUI renderers.

Manages the lifecycle and selection of renderers based on terminal
capabilities and user preferences.
"""
import logging
from typing import Dict, Optional, Any, List
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class RendererType(Enum):
    """Types of renderers available."""
    ASCII = "ascii"
    HYPERBOLIC_SLICE = "hyperbolic_slice"
    CURVATURE_FIELD = "curvature_field"
    GEODESIC_PATH = "geodesic_path"
    BOUNDARY_VISUAL = "boundary_visual"


class RenderMode(Enum):
    """Rendering modes."""
    WIREFRAME = "wireframe"
    FILLED = "filled"
    GRADIENT = "gradient"
    HEATMAP = "heatmap"
    ASCII_FALLBACK = "ascii_fallback"


@dataclass
class RendererCapabilities:
    """Capabilities of a renderer."""
    supports_color: bool = False
    supports_unicode: bool = False
    supports_gradients: bool = False
    supports_transparency: bool = False
    max_resolution: tuple = (80, 24)
    min_resolution: tuple = (40, 12)


@dataclass
class RendererRegistration:
    """Registration record for a renderer."""
    renderer_type: RendererType
    renderer_class: type
    capabilities: RendererCapabilities
    priority: int = 0  # Higher priority = preferred
    enabled: bool = True


class RendererRegistry:
    """
    Central registry for managing TUI renderers.

    Responsibilities:
    - Register available renderers
    - Select appropriate renderer based on capabilities
    - Manage renderer instances
    - Handle fallbacks
    """

    def __init__(self):
        self._renderers: Dict[RendererType, RendererRegistration] = {}
        self._instances: Dict[RendererType, Any] = {}
        self._terminal_capabilities: Optional[RendererCapabilities] = None

    def register_renderer(
        self,
        renderer_type: RendererType,
        renderer_class: type,
        capabilities: RendererCapabilities,
        priority: int = 0
    ) -> None:
        """
        Register a renderer.

        Args:
            renderer_type: Type of renderer
            renderer_class: The renderer class
            capabilities: Renderer capabilities
            priority: Selection priority (higher = preferred)
        """
        self._renderers[renderer_type] = RendererRegistration(
            renderer_type=renderer_type,
            renderer_class=renderer_class,
            capabilities=capabilities,
            priority=priority
        )
        logger.info(f"Registered renderer: {renderer_type.value} (priority: {priority})")

    def set_terminal_capabilities(self, capabilities: RendererCapabilities) -> None:
        """Set the detected terminal capabilities."""
        self._terminal_capabilities = capabilities
        logger.info(f"Terminal capabilities set: {capabilities}")

    def get_renderer(
        self,
        renderer_type: RendererType,
        mode: RenderMode = RenderMode.FILLED,
        force: bool = False
    ) -> Optional[Any]:
        """
        Get a renderer instance.

        Args:
            renderer_type: Type of renderer to get
            mode: Rendering mode
            force: Force creation even if capabilities don't match

        Returns:
            Renderer instance or None if unavailable
        """
        # Check if renderer is registered
        if renderer_type not in self._renderers:
            logger.warning(f"Renderer {renderer_type.value} not registered")
            return None

        registration = self._renderers[renderer_type]

        # Check if enabled
        if not registration.enabled:
            logger.warning(f"Renderer {renderer_type.value} is disabled")
            return None

        # Check capabilities match (unless forced)
        if not force and self._terminal_capabilities:
            if not self._capabilities_match(
                registration.capabilities,
                self._terminal_capabilities
            ):
                logger.warning(
                    f"Terminal capabilities insufficient for {renderer_type.value}"
                )
                return self._get_fallback_renderer(renderer_type)

        # Return cached instance or create new one
        if renderer_type not in self._instances:
            try:
                self._instances[renderer_type] = registration.renderer_class(mode=mode)
                logger.info(f"Created renderer instance: {renderer_type.value}")
            except Exception as e:
                logger.error(f"Failed to create renderer {renderer_type.value}: {e}")
                return self._get_fallback_renderer(renderer_type)

        return self._instances[renderer_type]

    def _capabilities_match(
        self,
        required: RendererCapabilities,
        available: RendererCapabilities
    ) -> bool:
        """Check if available capabilities meet requirements."""
        if required.supports_color and not available.supports_color:
            return False
        if required.supports_unicode and not available.supports_unicode:
            return False
        if required.supports_gradients and not available.supports_gradients:
            return False

        # Check resolution
        if available.max_resolution[0] < required.min_resolution[0]:
            return False
        if available.max_resolution[1] < required.min_resolution[1]:
            return False

        return True

    def _get_fallback_renderer(self, renderer_type: RendererType) -> Optional[Any]:
        """Get a fallback renderer (usually ASCII)."""
        # Try to get ASCII renderer as fallback
        if renderer_type != RendererType.ASCII:
            logger.info(f"Falling back to ASCII renderer for {renderer_type.value}")
            return self.get_renderer(RendererType.ASCII, force=True)
        return None

    def list_available_renderers(self) -> List[RendererType]:
        """List all available renderers that match terminal capabilities."""
        available = []
        for renderer_type, registration in self._renderers.items():
            if not registration.enabled:
                continue

            if self._terminal_capabilities:
                if self._capabilities_match(
                    registration.capabilities,
                    self._terminal_capabilities
                ):
                    available.append(renderer_type)
            else:
                available.append(renderer_type)

        # Sort by priority
        available.sort(
            key=lambda rt: self._renderers[rt].priority,
            reverse=True
        )
        return available

    def get_status(self) -> Dict[str, Any]:
        """Get registry status."""
        return {
            "registered_renderers": len(self._renderers),
            "active_instances": len(self._instances),
            "terminal_capabilities": self._terminal_capabilities,
            "renderers": {
                rt.value: {
                    "enabled": reg.enabled,
                    "priority": reg.priority,
                    "instantiated": rt in self._instances
                }
                for rt, reg in self._renderers.items()
            }
        }


# Global registry instance
_registry: Optional[RendererRegistry] = None


def get_renderer_registry() -> RendererRegistry:
    """Get the global renderer registry instance."""
    global _registry
    if _registry is None:
        _registry = RendererRegistry()
    return _registry
