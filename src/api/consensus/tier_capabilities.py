"""
Tier Capabilities API

Returns capabilities and limits for a service tier.
"""

from typing import Dict
import json
from pathlib import Path

class TierCapabilitiesProvider:
    """Provides tier capability information."""

    def __init__(self, capabilities_path: str = "consensus/tier_capabilities.json"):
        """Initialize with capabilities configuration."""
        self.capabilities_path = Path(capabilities_path)
        self.capabilities = self._load_capabilities()

    def _load_capabilities(self) -> Dict:
        """Load tier capabilities."""
        with open(self.capabilities_path, 'r') as f:
            return json.load(f)

    def get_tier_capabilities(self, tier_id: str) -> Dict:
        """
        Get capabilities for a specific tier.

        Args:
            tier_id: Service tier identifier

        Returns:
            Tier capabilities dictionary

        Raises:
            ValueError: If tier_id is invalid
        """
        if tier_id not in self.capabilities['capabilities']:
            raise ValueError(f"Invalid tier_id: {tier_id}")

        return self.capabilities['capabilities'][tier_id]

    def compare_tiers(self, tier_id_1: str, tier_id_2: str) -> Dict:
        """
        Compare capabilities of two tiers.

        Args:
            tier_id_1: First tier identifier
            tier_id_2: Second tier identifier

        Returns:
            Comparison dictionary
        """
        cap_1 = self.get_tier_capabilities(tier_id_1)
        cap_2 = self.get_tier_capabilities(tier_id_2)

        return {
            "tier_1": {
                "tier_id": tier_id_1,
                "mechanisms_count": cap_1['mechanisms_count'],
                "resource_limits": cap_1['resource_limits']
            },
            "tier_2": {
                "tier_id": tier_id_2,
                "mechanisms_count": cap_2['mechanisms_count'],
                "resource_limits": cap_2['resource_limits']
            },
            "differences": {
                "additional_mechanisms": cap_2['mechanisms_count'] - cap_1['mechanisms_count'],
                "node_limit_increase": "unlimited" if cap_2['resource_limits']['max_nodes'] is None else cap_2['resource_limits']['max_nodes'] - (cap_1['resource_limits']['max_nodes'] or 0)
            }
        }


def api_get_tier_capabilities(tier_id: str) -> Dict:
    """
    API endpoint to get tier capabilities.

    Args:
        tier_id: Service tier identifier

    Returns:
        JSON response with tier capabilities
    """
    try:
        provider = TierCapabilitiesProvider()
        capabilities = provider.get_tier_capabilities(tier_id)

        return {
            "status": "success",
            "tier_id": tier_id,
            "capabilities": capabilities
        }

    except ValueError as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": "invalid_tier"
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": "internal_error"
        }


# Example usage
if __name__ == "__main__":
    result = api_get_tier_capabilities("Advanced")
    print(json.dumps(result, indent=2))
