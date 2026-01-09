"""
Renderer Capability Detector - Detect terminal rendering capabilities.

Detects what the terminal can support for rendering (colors, unicode, etc.)
"""
import os
import sys
import logging
from typing import Optional

from hypersync.tui.renderers.renderer_registry import RendererCapabilities

logger = logging.getLogger(__name__)


class RendererCapabilityDetector:
    """Detects terminal rendering capabilities."""

    def __init__(self):
        self._capabilities: Optional[RendererCapabilities] = None

    def detect(self) -> RendererCapabilities:
        """
        Detect terminal capabilities.

        Returns:
            RendererCapabilities with detected features
        """
        if self._capabilities is not None:
            return self._capabilities

        logger.info("Detecting terminal rendering capabilities...")

        # Detect color support
        supports_color = self._detect_color_support()

        # Detect unicode support
        supports_unicode = self._detect_unicode_support()

        # Detect gradient support (requires 256 colors or truecolor)
        supports_gradients = self._detect_gradient_support()

        # Detect transparency (usually not supported in terminals)
        supports_transparency = False

        # Detect terminal size
        max_resolution = self._detect_terminal_size()

        self._capabilities = RendererCapabilities(
            supports_color=supports_color,
            supports_unicode=supports_unicode,
            supports_gradients=supports_gradients,
            supports_transparency=supports_transparency,
            max_resolution=max_resolution,
            min_resolution=(40, 12)
        )

        logger.info(f"Detected capabilities: {self._capabilities}")
        return self._capabilities

    def _detect_color_support(self) -> bool:
        """Detect if terminal supports colors."""
        # Check COLORTERM environment variable
        colorterm = os.getenv("COLORTERM", "")
        if colorterm in ("truecolor", "24bit"):
            return True

        # Check TERM environment variable
        term = os.getenv("TERM", "")
        if "256color" in term or "color" in term:
            return True

        # Check if stdout is a TTY
        if not sys.stdout.isatty():
            return False

        # Default to True for modern terminals
        return True

    def _detect_unicode_support(self) -> bool:
        """Detect if terminal supports unicode."""
        # Check encoding
        encoding = sys.stdout.encoding or ""
        if "utf" in encoding.lower():
            return True

        # Check LANG environment variable
        lang = os.getenv("LANG", "")
        if "utf" in lang.lower():
            return True

        # Try to encode a unicode character
        try:
            "█".encode(encoding)
            return True
        except (UnicodeEncodeError, LookupError):
            return False

    def _detect_gradient_support(self) -> bool:
        """Detect if terminal supports gradients (256 colors or better)."""
        colorterm = os.getenv("COLORTERM", "")
        if colorterm in ("truecolor", "24bit"):
            return True

        term = os.getenv("TERM", "")
        if "256color" in term:
            return True

        return False

    def _detect_terminal_size(self) -> tuple:
        """Detect terminal size."""
        try:
            import shutil
            size = shutil.get_terminal_size()
            return (size.columns, size.lines)
        except Exception:
            # Default size
            return (80, 24)

    def force_capabilities(self, capabilities: RendererCapabilities) -> None:
        """Force specific capabilities (for testing or overrides)."""
        self._capabilities = capabilities
        logger.info(f"Forced capabilities: {capabilities}")


# Global detector instance
_detector: Optional[RendererCapabilityDetector] = None


def get_capability_detector() -> RendererCapabilityDetector:
    """Get the global capability detector instance."""
    global _detector
    if _detector is None:
        _detector = RendererCapabilityDetector()
    return _detector


def detect_capabilities() -> RendererCapabilities:
    """Convenience function to detect capabilities."""
    return get_capability_detector().detect()
