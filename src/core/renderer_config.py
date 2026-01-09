"""
Renderer Configuration - Configuration management for renderers.
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class ColorScheme(Enum):
    """Color schemes for rendering."""
    MONOCHROME = "monochrome"
    BLUE_GRADIENT = "blue_gradient"
    HEAT_MAP = "heat_map"
    RAINBOW = "rainbow"
    CUSTOM = "custom"


@dataclass
class RenderConfig:
    """Configuration for a renderer."""

    # Display settings
    width: int = 80
    height: int = 24
    color_scheme: ColorScheme = ColorScheme.BLUE_GRADIENT
    use_unicode: bool = True
    use_color: bool = True

    # Hyperbolic geometry settings
    curvature: float = -1.0  # Negative for hyperbolic
    poincare_disk_radius: float = 1.0
    geodesic_resolution: int = 50

    # Rendering quality
    anti_alias: bool = False
    interpolation: str = "linear"  # linear, cubic, nearest

    # Performance
    max_fps: int = 30
    lazy_render: bool = True  # Only render on state change

    # Debug
    show_grid: bool = False
    show_axes: bool = False
    show_metrics: bool = False

    # Custom colors (for CUSTOM color scheme)
    custom_colors: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> 'RenderConfig':
        """Create configuration from environment variables."""
        return cls(
            width=int(os.getenv("HYPERSYNC_RENDER_WIDTH", "80")),
            height=int(os.getenv("HYPERSYNC_RENDER_HEIGHT", "24")),
            color_scheme=ColorScheme(
                os.getenv("HYPERSYNC_COLOR_SCHEME", "blue_gradient")
            ),
            use_unicode=os.getenv("HYPERSYNC_USE_UNICODE", "true").lower() == "true",
            use_color=os.getenv("HYPERSYNC_USE_COLOR", "true").lower() == "true",
            curvature=float(os.getenv("HYPERSYNC_CURVATURE", "-1.0")),
            max_fps=int(os.getenv("HYPERSYNC_MAX_FPS", "30")),
            show_grid=os.getenv("HYPERSYNC_SHOW_GRID", "false").lower() == "true",
            show_axes=os.getenv("HYPERSYNC_SHOW_AXES", "false").lower() == "true",
            show_metrics=os.getenv("HYPERSYNC_SHOW_METRICS", "false").lower() == "true"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "width": self.width,
            "height": self.height,
            "color_scheme": self.color_scheme.value,
            "use_unicode": self.use_unicode,
            "use_color": self.use_color,
            "curvature": self.curvature,
            "poincare_disk_radius": self.poincare_disk_radius,
            "geodesic_resolution": self.geodesic_resolution,
            "anti_alias": self.anti_alias,
            "interpolation": self.interpolation,
            "max_fps": self.max_fps,
            "lazy_render": self.lazy_render,
            "show_grid": self.show_grid,
            "show_axes": self.show_axes,
            "show_metrics": self.show_metrics,
            "custom_colors": self.custom_colors
        }


class ConfigManager:
    """Manages renderer configurations."""

    def __init__(self):
        self._configs: Dict[str, RenderConfig] = {}
        self._default_config = RenderConfig.from_env()

    def get_config(self, renderer_id: str) -> RenderConfig:
        """Get configuration for a renderer."""
        return self._configs.get(renderer_id, self._default_config)

    def set_config(self, renderer_id: str, config: RenderConfig) -> None:
        """Set configuration for a renderer."""
        self._configs[renderer_id] = config

    def get_default_config(self) -> RenderConfig:
        """Get default configuration."""
        return self._default_config

    def update_config(self, renderer_id: str, **kwargs) -> None:
        """Update specific config values."""
        config = self.get_config(renderer_id)
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        self._configs[renderer_id] = config


# Global config manager
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global config manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
