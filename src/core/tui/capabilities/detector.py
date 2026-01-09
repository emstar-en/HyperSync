"""
HyperSync TUI Capability Detector

Detects terminal capabilities via terminfo and runtime probes.
"""

import os
import sys
import subprocess
import logging
from typing import Dict, Any, Optional
from enum import Enum, auto


logger = logging.getLogger(__name__)


class ColorSupport(Enum):
    """Terminal color support levels."""
    NONE = auto()
    BASIC_8 = auto()
    EXTENDED_256 = auto()
    TRUE_COLOR = auto()


class TerminalTier(Enum):
    """Terminal capability tiers."""
    MICRO = auto()      # Minimal: 24x80, ASCII only
    SMALL = auto()      # Basic: 40x120, 8 colors
    STANDARD = auto()   # Standard: 60x160, 256 colors, Unicode
    LARGE = auto()      # Large: 80x200, true color, mouse
    ULTRA = auto()      # Ultra: 100+x240+, all features


class TerminalCapabilities:
    """Terminal capability information."""

    def __init__(self):
        self.term = os.environ.get('TERM', 'unknown')
        self.rows = 24
        self.cols = 80
        self.color_support = ColorSupport.NONE
        self.unicode_support = False
        self.mouse_support = False
        self.tier = TerminalTier.MICRO
        self.features = {}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "term": self.term,
            "rows": self.rows,
            "cols": self.cols,
            "color_support": self.color_support.name,
            "unicode_support": self.unicode_support,
            "mouse_support": self.mouse_support,
            "tier": self.tier.name,
            "features": self.features
        }


class CapabilityDetector:
    """
    Detects terminal capabilities.

    Uses terminfo database and runtime probes to determine what the
    terminal supports.
    """

    def __init__(self):
        self.capabilities = TerminalCapabilities()

    def detect(self) -> TerminalCapabilities:
        """
        Detect terminal capabilities.

        Returns:
            TerminalCapabilities instance
        """
        logger.info("Detecting terminal capabilities...")

        # Get terminal size
        self._detect_size()

        # Detect color support
        self._detect_color_support()

        # Detect Unicode support
        self._detect_unicode_support()

        # Detect mouse support
        self._detect_mouse_support()

        # Detect additional features
        self._detect_features()

        # Determine tier
        self._determine_tier()

        logger.info(f"Detected capabilities: {self.capabilities.to_dict()}")

        return self.capabilities

    def _detect_size(self):
        """Detect terminal size."""
        try:
            import shutil
            cols, rows = shutil.get_terminal_size()
            self.capabilities.rows = rows
            self.capabilities.cols = cols
        except Exception as e:
            logger.warning(f"Failed to detect terminal size: {e}")

    def _detect_color_support(self):
        """Detect color support level."""
        term = self.capabilities.term.lower()

        # Check for true color support
        if any(x in term for x in ['truecolor', '24bit', 'direct']):
            self.capabilities.color_support = ColorSupport.TRUE_COLOR
            return

        # Check COLORTERM environment variable
        colorterm = os.environ.get('COLORTERM', '').lower()
        if colorterm in ['truecolor', '24bit']:
            self.capabilities.color_support = ColorSupport.TRUE_COLOR
            return

        # Check for 256 color support
        if '256' in term or '256color' in term:
            self.capabilities.color_support = ColorSupport.EXTENDED_256
            return

        # Check for basic color support
        if 'color' in term or 'ansi' in term:
            self.capabilities.color_support = ColorSupport.BASIC_8
            return

        # Try tput
        try:
            result = subprocess.run(
                ['tput', 'colors'],
                capture_output=True,
                text=True,
                timeout=1
            )

            if result.returncode == 0:
                colors = int(result.stdout.strip())

                if colors >= 16777216:
                    self.capabilities.color_support = ColorSupport.TRUE_COLOR
                elif colors >= 256:
                    self.capabilities.color_support = ColorSupport.EXTENDED_256
                elif colors >= 8:
                    self.capabilities.color_support = ColorSupport.BASIC_8

        except Exception as e:
            logger.debug(f"tput colors failed: {e}")

    def _detect_unicode_support(self):
        """Detect Unicode support."""
        # Check locale
        locale = os.environ.get('LANG', '').lower()

        if 'utf' in locale or 'utf-8' in locale:
            self.capabilities.unicode_support = True
            return

        # Check terminal type
        term = self.capabilities.term.lower()
        if 'utf' in term:
            self.capabilities.unicode_support = True
            return

        # Try encoding test
        try:
            test_char = '█'
            test_char.encode(sys.stdout.encoding or 'utf-8')
            self.capabilities.unicode_support = True
        except Exception:
            self.capabilities.unicode_support = False

    def _detect_mouse_support(self):
        """Detect mouse support."""
        term = self.capabilities.term.lower()

        # Most modern terminals support mouse
        if any(x in term for x in ['xterm', 'screen', 'tmux', 'rxvt', 'konsole', 'gnome']):
            self.capabilities.mouse_support = True

    def _detect_features(self):
        """Detect additional terminal features."""
        features = {}

        # Detect alternate screen support
        try:
            result = subprocess.run(
                ['tput', 'smcup'],
                capture_output=True,
                timeout=1
            )
            features['alternate_screen'] = result.returncode == 0
        except Exception:
            features['alternate_screen'] = False

        # Detect cursor visibility control
        try:
            result = subprocess.run(
                ['tput', 'civis'],
                capture_output=True,
                timeout=1
            )
            features['cursor_control'] = result.returncode == 0
        except Exception:
            features['cursor_control'] = False

        # Detect bold/underline support
        features['bold'] = self.capabilities.color_support != ColorSupport.NONE
        features['underline'] = self.capabilities.color_support != ColorSupport.NONE

        self.capabilities.features = features

    def _determine_tier(self):
        """Determine terminal tier based on capabilities."""
        rows = self.capabilities.rows
        cols = self.capabilities.cols
        color = self.capabilities.color_support
        unicode = self.capabilities.unicode_support
        mouse = self.capabilities.mouse_support

        # ULTRA: 100+ rows, 240+ cols, true color, Unicode, mouse
        if rows >= 100 and cols >= 240 and color == ColorSupport.TRUE_COLOR and unicode and mouse:
            self.capabilities.tier = TerminalTier.ULTRA

        # LARGE: 80+ rows, 200+ cols, true color, Unicode
        elif rows >= 80 and cols >= 200 and color == ColorSupport.TRUE_COLOR and unicode:
            self.capabilities.tier = TerminalTier.LARGE

        # STANDARD: 60+ rows, 160+ cols, 256 colors, Unicode
        elif rows >= 60 and cols >= 160 and color in [ColorSupport.EXTENDED_256, ColorSupport.TRUE_COLOR] and unicode:
            self.capabilities.tier = TerminalTier.STANDARD

        # SMALL: 40+ rows, 120+ cols, 8 colors
        elif rows >= 40 and cols >= 120 and color != ColorSupport.NONE:
            self.capabilities.tier = TerminalTier.SMALL

        # MICRO: Everything else
        else:
            self.capabilities.tier = TerminalTier.MICRO


def detect_capabilities() -> TerminalCapabilities:
    """Detect terminal capabilities."""
    detector = CapabilityDetector()
    return detector.detect()
