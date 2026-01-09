"""
Resource Validation Middleware

Middleware to validate resource requirements against tier limits.
"""

from typing import Dict
import json
from pathlib import Path

class ResourceValidationMiddleware:
    """Validates resource requirements against tier limits."""

    def __init__(self,
                 profiles_path: str = "consensus/mechanism_profiles.json",
                 mapping_path: str = "consensus/tier_mapping.json"):
        """Initialize with configuration paths."""
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

    def validate_resources(self, mechanism_id: str, tier_id: str) -> Dict:
        """
        Validate mechanism resources against tier limits.

        Args:
            mechanism_id: Mechanism identifier
            tier_id: Service tier identifier

        Returns:
            Validation result dictionary
        """
        if mechanism_id not in self.profiles['profiles']:
            return {
                "valid": False,
                "errors": [f"Unknown mechanism: {mechanism_id}"]
            }

        if tier_id not in self.mapping['tiers']:
            return {
                "valid": False,
                "errors": [f"Unknown tier: {tier_id}"]
            }

        profile = self.profiles['profiles'][mechanism_id]
        tier_data = self.mapping['tiers'][tier_id]

        resources = profile['resources']
        tier_resources = tier_data.get('resource_profile', {})

        errors = []
        warnings = []

        # GPU validation
        if resources.get('gpu_required', False):
            if tier_resources.get('gpu_budget_ms', 0) == 0:
                errors.append("Mechanism requires GPU but tier has no GPU allocation")
            elif 'gpu_memory_mb' in resources:
                # Check if tier can support GPU memory requirements
                if resources['gpu_memory_mb'] > 4096 and tier_resources.get('gpu_budget_ms', 0) < 500:
                    warnings.append(f"Mechanism requires {resources['gpu_memory_mb']}MB GPU memory with limited GPU budget")

        # Memory validation
        if 'memory_budget_mb' in tier_resources:
            if resources['memory_mb_min'] > tier_resources['memory_budget_mb']:
                errors.append(
                    f"Mechanism requires {resources['memory_mb_min']}MB but tier limit is {tier_resources['memory_budget_mb']}MB"
                )
            elif resources['memory_mb_recommended'] > tier_resources['memory_budget_mb']:
                warnings.append(
                    f"Mechanism recommends {resources['memory_mb_recommended']}MB but tier limit is {tier_resources['memory_budget_mb']}MB"
                )

        # CPU validation
        if resources['cpu_cores_min'] > 16:
            if tier_resources.get('time_budget_ms', 1000) < 600:
                warnings.append(
                    f"Mechanism requires {resources['cpu_cores_min']} CPU cores with tight time budget"
                )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "mechanism_id": mechanism_id,
            "tier_id": tier_id
        }

    def enforce(self, mechanism_id: str, tier_id: str) -> None:
        """
        Enforce resource validation.

        Args:
            mechanism_id: Mechanism identifier
            tier_id: Service tier identifier

        Raises:
            ValueError: If validation fails
        """
        result = self.validate_resources(mechanism_id, tier_id)
        if not result['valid']:
            raise ValueError(f"Resource validation failed: {', '.join(result['errors'])}")


# Example usage
if __name__ == "__main__":
    middleware = ResourceValidationMiddleware()

    # Test resource validation
    result = middleware.validate_resources("raft", "PRO")
    print(f"Raft resources for PRO: {result}")

    result = middleware.validate_resources("geometric_consensus", "CORE")
    print(f"Geometric Consensus resources for CORE: {result}")
