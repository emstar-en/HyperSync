"""
Tier Enforcement Middleware

Middleware to enforce tier-based access control for consensus mechanisms.
"""

from typing import Dict, Callable
from functools import wraps
import json
from pathlib import Path

class TierEnforcementMiddleware:
    """Enforces tier-based access control."""

    def __init__(self, mapping_path: str = "consensus/tier_mapping.json"):
        """Initialize with tier mapping."""
        self.mapping_path = Path(mapping_path)
        self.mapping = self._load_mapping()

    def _load_mapping(self) -> Dict:
        """Load tier mapping."""
        with open(self.mapping_path, 'r') as f:
            return json.load(f)

    def check_mechanism_access(self, mechanism_id: str, tier_id: str) -> Dict:
        """
        Check if a tier has access to a mechanism.

        Args:
            mechanism_id: Mechanism identifier
            tier_id: Service tier identifier

        Returns:
            Access check result
        """
        if tier_id not in self.mapping['tiers']:
            return {
                "allowed": False,
                "reason": f"Invalid tier: {tier_id}"
            }

        tier_data = self.mapping['tiers'][tier_id]
        tier_mechanisms = [m['id'] for m in tier_data['mechanisms']]

        # Check direct access
        if mechanism_id in tier_mechanisms:
            return {
                "allowed": True,
                "reason": "Direct access"
            }

        # Check inherited access
        if 'inherits_from' in tier_data:
            parent_check = self.check_mechanism_access(mechanism_id, tier_data['inherits_from'])
            if parent_check['allowed']:
                return {
                    "allowed": True,
                    "reason": f"Inherited from {tier_data['inherits_from']}"
                }

        return {
            "allowed": False,
            "reason": f"Mechanism '{mechanism_id}' not available for tier '{tier_id}'"
        }

    def enforce(self, mechanism_id: str, tier_id: str) -> None:
        """
        Enforce tier access control.

        Args:
            mechanism_id: Mechanism identifier
            tier_id: Service tier identifier

        Raises:
            PermissionError: If access is denied
        """
        check = self.check_mechanism_access(mechanism_id, tier_id)
        if not check['allowed']:
            raise PermissionError(check['reason'])


def require_tier_access(mechanism_id_param: str = "mechanism_id", tier_id_param: str = "tier_id"):
    """
    Decorator to enforce tier access control on API endpoints.

    Args:
        mechanism_id_param: Name of mechanism_id parameter
        tier_id_param: Name of tier_id parameter

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract mechanism_id and tier_id from kwargs
            mechanism_id = kwargs.get(mechanism_id_param)
            tier_id = kwargs.get(tier_id_param)

            if not mechanism_id or not tier_id:
                return {
                    "status": "error",
                    "error": "Missing mechanism_id or tier_id",
                    "error_type": "missing_parameters"
                }

            # Check access
            middleware = TierEnforcementMiddleware()
            try:
                middleware.enforce(mechanism_id, tier_id)
            except PermissionError as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "error_type": "permission_denied"
                }

            # Call original function
            return func(*args, **kwargs)

        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    middleware = TierEnforcementMiddleware()

    # Test access check
    result = middleware.check_mechanism_access("raft", "PRO")
    print(f"Raft access for PRO: {result}")

    result = middleware.check_mechanism_access("geometric_consensus", "CORE")
    print(f"Geometric Consensus access for CORE: {result}")
