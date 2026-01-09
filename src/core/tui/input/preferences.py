"""
HyperSync TUI Preferences Manager

Operator preference persistence and management.
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path


logger = logging.getLogger(__name__)


class PreferencesManager:
    """
    Preferences manager.

    Manages operator preferences with schema-driven validation.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".hypersync" / "tui"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.preferences: Dict[str, Any] = {}
        logger.info(f"PreferencesManager initialized: {self.config_dir}")

    def load(self, operator_id: str) -> Dict[str, Any]:
        """Load preferences for operator."""
        prefs_file = self.config_dir / f"{operator_id}.json"

        if prefs_file.exists():
            try:
                with open(prefs_file, 'r') as f:
                    self.preferences = json.load(f)
                logger.info(f"Loaded preferences for {operator_id}")
            except Exception as e:
                logger.error(f"Failed to load preferences: {e}")
                self.preferences = self._get_defaults()
        else:
            self.preferences = self._get_defaults()

        return self.preferences

    def save(self, operator_id: str):
        """Save preferences for operator."""
        prefs_file = self.config_dir / f"{operator_id}.json"

        try:
            with open(prefs_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
            logger.info(f"Saved preferences for {operator_id}")
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get preference value."""
        return self.preferences.get(key, default)

    def set(self, key: str, value: Any):
        """Set preference value."""
        self.preferences[key] = value

    def _get_defaults(self) -> Dict[str, Any]:
        """Get default preferences."""
        return {
            "accessibility_mode": "DEFAULT",
            "layout_template": "monitoring",
            "color_scheme": "default",
            "mouse_enabled": True,
            "key_bindings": {
                "quit": "q",
                "help": "?",
                "refresh": "r"
            },
            "panel_preferences": {}
        }

    def export_preferences(self, filepath: Path):
        """Export preferences to file."""
        with open(filepath, 'w') as f:
            json.dump(self.preferences, f, indent=2)
        logger.info(f"Exported preferences to {filepath}")

    def import_preferences(self, filepath: Path):
        """Import preferences from file."""
        with open(filepath, 'r') as f:
            self.preferences = json.load(f)
        logger.info(f"Imported preferences from {filepath}")
