"""
List Available Consensus Mechanisms API

Returns consensus mechanisms available for the user's service tier.
"""

from typing import List, Dict, Optional
import json
from pathlib import Path

class ConsensusMechanismLister:
    """Lists available consensus mechanisms based on tier."""

    def __init__(self, tier_mapping_path: str = "consensus/tier_mapping.json"):
        """Initialize with tier mapping configuration."""
        self.tier_mapping_path = Path(tier_mapping_path)
        self.tier_mapping = self._load_tier_mapping()

    def _load_tier_mapping(self) -> Dict:
        """Load tier mapping from JSON file."""
        with open(self.tier_mapping_path, 'r') as f:
            return json.load(f)

    def list_mechanisms(self, tier_id: str, include_inherited: bool = True) -> List[Dict]:
        """
        List consensus mechanisms available for a tier.

        Args:
            tier_id: Service tier identifier (e.g., "CORE", "PRO", "Advanced")
            include_inherited: Include mechanisms from lower tiers

        Returns:
            List of mechanism dictionaries with id, name, weight, and use case

        Raises:
            ValueError: If tier_id is invalid
        """
        if tier_id not in self.tier_mapping['tiers']:
            raise ValueError(f"Invalid tier_id: {tier_id}")

        tier_data = self.tier_mapping['tiers'][tier_id]
        mechanisms = tier_data['mechanisms'].copy()

        # Add inherited mechanisms if requested
        if include_inherited and 'inherits_from' in tier_data:
            parent_tier = tier_data['inherits_from']
            parent_mechanisms = self.list_mechanisms(parent_tier, include_inherited=True)
            mechanisms.extend(parent_mechanisms)

        return mechanisms

    def list_all_mechanisms(self) -> List[Dict]:
        """List all consensus mechanisms across all tiers."""
        all_mechanisms = {}

        for tier_id, tier_data in self.tier_mapping['tiers'].items():
            for mechanism in tier_data['mechanisms']:
                if mechanism['id'] not in all_mechanisms:
                    all_mechanisms[mechanism['id']] = mechanism

        return list(all_mechanisms.values())

    def get_mechanism_tiers(self, mechanism_id: str) -> List[str]:
        """
        Get list of tiers that have access to a specific mechanism.

        Args:
            mechanism_id: Mechanism identifier

        Returns:
            List of tier IDs that can use this mechanism
        """
        tiers = []

        for tier_id, tier_data in self.tier_mapping['tiers'].items():
            tier_mechanisms = self.list_mechanisms(tier_id, include_inherited=True)
            if any(m['id'] == mechanism_id for m in tier_mechanisms):
                tiers.append(tier_id)

        return tiers


def api_list_mechanisms(tier_id: str, include_inherited: bool = True) -> Dict:
    """
    API endpoint to list available consensus mechanisms.

    Args:
        tier_id: User's service tier
        include_inherited: Include mechanisms from lower tiers

    Returns:
        JSON response with mechanisms list
    """
    try:
        lister = ConsensusMechanismLister()
        mechanisms = lister.list_mechanisms(tier_id, include_inherited)

        return {
            "status": "success",
            "tier_id": tier_id,
            "total_mechanisms": len(mechanisms),
            "mechanisms": mechanisms,
            "include_inherited": include_inherited
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
    # List mechanisms for PRO tier
    result = api_list_mechanisms("PRO", include_inherited=True)
    print(json.dumps(result, indent=2))
