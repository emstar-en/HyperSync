"""
Validate Consensus Mechanism Configuration API

Validates mechanism configuration without applying it.
"""

from typing import Dict
import json
from pathlib import Path

class MechanismConfigValidator:
    """Validates consensus mechanism configurations."""

    def __init__(self,
                 profiles_path: str = "consensus/mechanism_profiles.json",
                 mapping_path: str = "consensus/tier_mapping.json"):
        """Initialize validator with configuration paths."""
        self.profiles_path = Path(profiles_path)
        self.mapping_path = Path(mapping_path)
        self.profiles = self._load_profiles()
        self.mapping = self._load_mapping()

    def _load_profiles(self) -> Dict:
        """Load mechanism profiles."""
        with open(self.profiles_path, 'r') as f:
            return json.load(f)

    def _load_mapping(self) -> Dict:
        """Load tier mapping."""
        with open(self.mapping_path, 'r') as f:
            return json.load(f)

    def validate_config(self, mechanism_id: str, tier_id: str, config: Dict) -> Dict:
        """
        Validate a mechanism configuration.

        Args:
            mechanism_id: Mechanism identifier
            tier_id: Service tier
            config: Configuration to validate

        Returns:
            Validation result dictionary
        """
        validation_errors = []
        validation_warnings = []

        # Check mechanism exists
        if mechanism_id not in self.profiles['profiles']:
            validation_errors.append(f"Unknown mechanism: {mechanism_id}")
            return {
                "valid": False,
                "errors": validation_errors,
                "warnings": validation_warnings
            }

        # Check tier exists
        if tier_id not in self.mapping['tiers']:
            validation_errors.append(f"Unknown tier: {tier_id}")
            return {
                "valid": False,
                "errors": validation_errors,
                "warnings": validation_warnings
            }

        profile = self.profiles['profiles'][mechanism_id]
        tier_data = self.mapping['tiers'][tier_id]

        # Validate resource requirements
        resources = profile['resources']
        tier_resources = tier_data.get('resource_profile', {})

        # GPU check
        if resources.get('gpu_required', False):
            if tier_resources.get('gpu_budget_ms', 0) == 0:
                validation_errors.append("Mechanism requires GPU but tier has no GPU budget")

        # Memory check
        if 'memory_budget_mb' in tier_resources:
            if resources['memory_mb_min'] > tier_resources['memory_budget_mb']:
                validation_errors.append(
                    f"Mechanism requires {resources['memory_mb_min']}MB but tier limit is {tier_resources['memory_budget_mb']}MB"
                )

        # CPU check
        if 'time_budget_ms' in tier_resources:
            # This is a soft check - warn if might be tight
            if resources['cpu_cores_min'] > 4 and tier_resources['time_budget_ms'] < 600:
                validation_warnings.append(
                    f"Mechanism requires {resources['cpu_cores_min']} CPU cores with tight time budget"
                )

        # Config-specific validation
        if config:
            # Validate config keys (mechanism-specific)
            if 'timeout_ms' in config:
                if not isinstance(config['timeout_ms'], int) or config['timeout_ms'] < 0:
                    validation_errors.append("timeout_ms must be a positive integer")

            if 'quorum_size' in config:
                if not isinstance(config['quorum_size'], int) or config['quorum_size'] < 1:
                    validation_errors.append("quorum_size must be a positive integer")

        return {
            "valid": len(validation_errors) == 0,
            "errors": validation_errors,
            "warnings": validation_warnings,
            "mechanism_id": mechanism_id,
            "tier_id": tier_id
        }


def api_validate_mechanism_config(mechanism_id: str, tier_id: str, config: Dict) -> Dict:
    """
    API endpoint to validate mechanism configuration.

    Args:
        mechanism_id: Mechanism identifier
        tier_id: Service tier
        config: Configuration to validate

    Returns:
        JSON response with validation result
    """
    try:
        validator = MechanismConfigValidator()
        result = validator.validate_config(mechanism_id, tier_id, config)

        return {
            "status": "success",
            **result
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": "internal_error"
        }


# Example usage
if __name__ == "__main__":
    config = {
        "timeout_ms": 5000,
        "quorum_size": 3
    }
    result = api_validate_mechanism_config("raft", "PRO", config)
    print(json.dumps(result, indent=2))
