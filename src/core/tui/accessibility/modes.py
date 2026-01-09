"""
HyperSync TUI Accessibility Modes

Accessibility packs with palettes, overlays, and screen-reader support.
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum, auto
from dataclasses import dataclass


logger = logging.getLogger(__name__)


class AccessibilityMode(Enum):
    """Accessibility modes."""
    DEFAULT = auto()
    MONOCHROME = auto()
    HIGH_CONTRAST = auto()
    SCREEN_READER = auto()
    FOCUS_MODE = auto()


@dataclass
class ColorPalette:
    """Color palette definition."""
    name: str
    foreground: str
    background: str
    accent: str
    warning: str
    error: str
    success: str


class AccessibilityManager:
    """
    Accessibility manager.

    Manages accessibility modes, palettes, and overlays.
    """

    def __init__(self):
        self.current_mode = AccessibilityMode.DEFAULT
        self.palettes = self._init_palettes()
        self.screen_reader_enabled = False
        self.focus_mode_enabled = False
        logger.info("AccessibilityManager initialized")

    def _init_palettes(self) -> Dict[AccessibilityMode, ColorPalette]:
        """Initialize color palettes."""
        return {
            AccessibilityMode.DEFAULT: ColorPalette(
                name="Default",
                foreground="white",
                background="black",
                accent="cyan",
                warning="yellow",
                error="red",
                success="green"
            ),
            AccessibilityMode.MONOCHROME: ColorPalette(
                name="Monochrome",
                foreground="white",
                background="black",
                accent="white",
                warning="white",
                error="white",
                success="white"
            ),
            AccessibilityMode.HIGH_CONTRAST: ColorPalette(
                name="High Contrast",
                foreground="white",
                background="black",
                accent="yellow",
                warning="yellow",
                error="red",
                success="green"
            ),
            AccessibilityMode.SCREEN_READER: ColorPalette(
                name="Screen Reader",
                foreground="white",
                background="black",
                accent="cyan",
                warning="yellow",
                error="red",
                success="green"
            ),
            AccessibilityMode.FOCUS_MODE: ColorPalette(
                name="Focus Mode",
                foreground="white",
                background="black",
                accent="blue",
                warning="yellow",
                error="red",
                success="green"
            )
        }

    def set_mode(self, mode: AccessibilityMode):
        """Set accessibility mode."""
        self.current_mode = mode

        if mode == AccessibilityMode.SCREEN_READER:
            self.screen_reader_enabled = True
        else:
            self.screen_reader_enabled = False

        if mode == AccessibilityMode.FOCUS_MODE:
            self.focus_mode_enabled = True
        else:
            self.focus_mode_enabled = False

        logger.info(f"Accessibility mode set to: {mode.name}")

    def get_palette(self) -> ColorPalette:
        """Get current color palette."""
        return self.palettes[self.current_mode]

    def generate_aria_hints(self, panel_type: str, state: Dict[str, Any]) -> str:
        """Generate ARIA-style hints for screen readers."""
        if panel_type == "live_anchor":
            anchors = state.get("anchors", [])
            anomalies = sum(1 for a in anchors if a.get("anomaly", False))
            return f"Live anchors panel. {len(anchors)} anchors, {anomalies} anomalies detected."

        elif panel_type == "activity_curve":
            activity = state.get("activity", [])
            if activity:
                avg = sum(activity) / len(activity)
                max_val = max(activity)
                return f"Geodesic activity curve. Average: {avg:.2f}, Maximum: {max_val:.2f}"
            return "Geodesic activity curve. No data."

        return f"{panel_type} panel"


def get_accessibility_manager() -> AccessibilityManager:
    """Get global accessibility manager."""
    global _accessibility_manager
    if '_accessibility_manager' not in globals():
        globals()['_accessibility_manager'] = AccessibilityManager()
    return globals()['_accessibility_manager']
