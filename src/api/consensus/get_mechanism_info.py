"""
Get Consensus Mechanism Info API

Returns detailed information about a specific consensus mechanism.
"""

from typing import Dict, Optional
import json
from pathlib import Path

class MechanismInfoProvider:
    """Provides detailed information about consensus mechanisms."""

    def __init__(self, 
                 profiles_path: str = "consensus/mechanism_profiles.json",
                 mapping_path: str = "consensus/tier_mapping.json"):
        """Initialize with configuration paths."""
        self.profiles_path = Path(profiles_path)
        self.mapping_path = Path(mapping_path)
        self.profiles = self._load_profiles()
        self.mapping = self._load_mapping()

    def _load_profiles(self) -> Dict:
        """Load mechanism profiles from JSON file."""
        with open(self.profiles_path, 'r') as f:
            return json.load(f)

    def _load_mapping(self) -> Dict:
        """Load tier mapping from JSON file."""
        with open(self.mapping_path, 'r') as f:
            return json.load(f)

    def get_mechanism_info(self, mechanism_id: str) -> Dict:
        """
        Get detailed information about a consensus mechanism.

        Args:
            mechanism_id: Mechanism identifier

        Returns:
            Dictionary with mechanism details including resources, scalability, etc.

        Raises:
            ValueError: If mechanism_id is invalid
        """
        if mechanism_id not in self.profiles['profiles']:
            raise ValueError(f"Invalid mechanism_id: {mechanism_id}")

        profile = self.profiles['profiles'][mechanism_id]

        # Find which tiers have access to this mechanism
        available_tiers = []
        for tier_id, tier_data in self.mapping['tiers'].items():
            tier_mechanisms = [m['id'] for m in tier_data['mechanisms']]
            if mechanism_id in tier_mechanisms:
                available_tiers.append({
                    "tier_id": tier_id,
                    "tier_position": tier_data['tier_position'],
                    "display_name": tier_data['display_name']
                })

        # Sort by tier position
        available_tiers.sort(key=lambda x: x['tier_position'])

        return {
            **profile,
            "available_in_tiers": available_tiers,
            "minimum_tier": available_tiers[0] if available_tiers else None
        }

    def compare_mechanisms(self, mechanism_id_1: str, mechanism_id_2: str) -> Dict:
        """
        Compare two consensus mechanisms.

        Args:
            mechanism_id_1: First mechanism identifier
            mechanism_id_2: Second mechanism identifier

        Returns:
            Comparison dictionary
        """
        info_1 = self.get_mechanism_info(mechanism_id_1)
        info_2 = self.get_mechanism_info(mechanism_id_2)

        return {
            "mechanism_1": {
                "id": mechanism_id_1,
                "name": info_1['name'],
                "weight": info_1['weight'],
                "resources": info_1['resources']
            },
            "mechanism_2": {
                "id": mechanism_id_2,
                "name": info_2['name'],
                "weight": info_2['weight'],
                "resources": info_2['resources']
            },
            "comparison": {
                "lighter": mechanism_id_1 if self._weight_value(info_1['weight']) < self._weight_value(info_2['weight']) else mechanism_id_2,
                "more_cpu_intensive": mechanism_id_1 if info_1['resources']['cpu_cores_min'] > info_2['resources']['cpu_cores_min'] else mechanism_id_2,
                "more_memory_intensive": mechanism_id_1 if info_1['resources']['memory_mb_min'] > info_2['resources']['memory_mb_min'] else mechanism_id_2
            }
        }

    def _weight_value(self, weight: str) -> int:
        """Convert weight string to numeric value for comparison."""
        weights = {
            "lightweight": 1,
            "light": 2,
            "moderate": 3,
            "heavy": 4,
            "very_heavy": 5
        }
        return weights.get(weight, 0)


def api_get_mechanism_info(mechanism_id: str) -> Dict:
    """
    API endpoint to get mechanism information.

    Args:
        mechanism_id: Mechanism identifier

    Returns:
        JSON response with mechanism details
    """
    try:
        provider = MechanismInfoProvider()
        info = provider.get_mechanism_info(mechanism_id)

        return {
            "status": "success",
            "mechanism_id": mechanism_id,
            "info": info
        }

    except ValueError as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": "invalid_mechanism"
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": "internal_error"
        }


# Example usage
if __name__ == "__main__":
    # Get info for Raft mechanism
    result = api_get_mechanism_info("raft")
    print(json.dumps(result, indent=2))
