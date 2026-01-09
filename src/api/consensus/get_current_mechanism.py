"""
Get Current Consensus Mechanism API

Returns the currently active consensus mechanism configuration.
"""

from typing import Dict, Optional
import json
from pathlib import Path

class CurrentMechanismProvider:
    """Provides information about the currently active consensus mechanism."""

    def __init__(self, config_path: str = "config/consensus/active_mechanism.json"):
        """Initialize with configuration path."""
        self.config_path = Path(config_path)

    def get_current_mechanism(self) -> Optional[Dict]:
        """
        Get the currently active consensus mechanism.

        Returns:
            Current mechanism configuration or None if not set
        """
        if not self.config_path.exists():
            return None

        with open(self.config_path, 'r') as f:
            return json.load(f)

    def is_mechanism_active(self) -> bool:
        """Check if a consensus mechanism is currently active."""
        return self.config_path.exists()

    def get_mechanism_status(self) -> Dict:
        """
        Get detailed status of the current mechanism.

        Returns:
            Status dictionary with mechanism details and health info
        """
        current = self.get_current_mechanism()

        if not current:
            return {
                "active": False,
                "message": "No consensus mechanism currently selected"
            }

        return {
            "active": True,
            "mechanism_id": current['mechanism_id'],
            "mechanism_name": current['mechanism_name'],
            "tier_id": current['tier_id'],
            "selected_at": current['selected_at'],
            "config": current.get('config', {}),
            "validation": current.get('validation', {})
        }


def api_get_current_mechanism() -> Dict:
    """
    API endpoint to get current consensus mechanism.

    Returns:
        JSON response with current mechanism info
    """
    try:
        provider = CurrentMechanismProvider()
        status = provider.get_mechanism_status()

        return {
            "status": "success",
            **status
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": "internal_error"
        }


# Example usage
if __name__ == "__main__":
    result = api_get_current_mechanism()
    print(json.dumps(result, indent=2))
