"""
Panel Registry Integration - Wire enhanced panels into registry.

This file shows the changes needed to hypersync/tui/panels/registry.py
"""

# ADD THESE IMPORTS at the top of hypersync/tui/panels/registry.py:
# from hypersync.tui.panels.hyperbolic.enhanced_slice_viewer import EnhancedSliceViewerPanel
# from hypersync.tui.renderers.renderer_registry import get_renderer_registry, RendererType
# from hypersync.tui.renderers.renderer_config import get_config_manager
# from hypersync.tui.capabilities.renderer_detector import detect_capabilities

# ADD THIS INITIALIZATION CODE to the registry initialization:

def initialize_renderer_system():
    """
    Initialize the renderer system with capability detection.

    Call this during TUI startup, before creating panels.
    """
    import logging
    from hypersync.tui.renderers.renderer_registry import (
        get_renderer_registry,
        RendererType,
        RendererCapabilities
    )
    from hypersync.tui.capabilities.renderer_detector import detect_capabilities

    logger = logging.getLogger(__name__)

    # Detect terminal capabilities
    capabilities = detect_capabilities()

    # Get registry
    registry = get_renderer_registry()
    registry.set_terminal_capabilities(capabilities)

    # Register renderers
    logger.info("Registering renderers...")

    # Import renderer classes
    from hypersync.tui.renderers.hyperbolic_slice_renderer import HyperbolicSliceRenderer
    from hypersync.tui.renderers.curvature_field_renderer import CurvatureFieldRenderer

    # Register hyperbolic slice renderer
    registry.register_renderer(
        RendererType.HYPERBOLIC_SLICE,
        HyperbolicSliceRenderer,
        RendererCapabilities(
            supports_color=True,
            supports_unicode=True,
            supports_gradients=True,
            min_resolution=(60, 20)
        ),
        priority=10
    )

    # Register curvature field renderer
    registry.register_renderer(
        RendererType.CURVATURE_FIELD,
        CurvatureFieldRenderer,
        RendererCapabilities(
            supports_color=True,
            supports_unicode=True,
            supports_gradients=True,
            min_resolution=(60, 20)
        ),
        priority=10
    )

    # Register ASCII fallback (always available)
    from hypersync.tui.renderers.ascii_renderer import ASCIIRenderer
    registry.register_renderer(
        RendererType.ASCII,
        ASCIIRenderer,
        RendererCapabilities(
            supports_color=False,
            supports_unicode=False,
            min_resolution=(40, 12)
        ),
        priority=1  # Low priority, used as fallback
    )

    logger.info(f"Renderer system initialized with {len(registry.list_available_renderers())} available renderers")


# MODIFY PANEL REGISTRATION to use enhanced panels:

def register_enhanced_panels(panel_registry):
    """
    Register enhanced panels with renderer support.

    Args:
        panel_registry: The panel registry instance
    """
    # Create enhanced slice viewer
    slice_viewer = EnhancedSliceViewerPanel(panel_id="hyperbolic_slice")

    # Register it
    panel_registry.register_panel(
        panel_id="hyperbolic_slice",
        panel_instance=slice_viewer,
        title="Hyperbolic Slice",
        default_size=(80, 30),
        resizable=True
    )

    # Register other enhanced panels as they're created...


# EXAMPLE: Updated panel registry initialization

class PanelRegistry:
    """Registry for TUI panels."""

    def __init__(self):
        self._panels = {}

        # Initialize renderer system first
        initialize_renderer_system()

        # Register enhanced panels
        register_enhanced_panels(self)

    def register_panel(self, panel_id, panel_instance, title, default_size, resizable=True):
        """Register a panel."""
        self._panels[panel_id] = {
            "instance": panel_instance,
            "title": title,
            "default_size": default_size,
            "resizable": resizable
        }

    def get_panel(self, panel_id):
        """Get a panel instance."""
        return self._panels.get(panel_id, {}).get("instance")
