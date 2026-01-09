"""
Policy & Governance Wiring - Integrates policy enforcement across all operations.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PolicyGovernanceIntegration:
    """Wires policy enforcement into all decision points."""

    def __init__(self):
        self._policies = {}
        self._audit_log = []

    def register_policy(self, policy_id, policy):
        """Register governance policy."""
        self._policies[policy_id] = policy
        logger.info(f"Registered policy: {policy_id}")

    def enforce(self, operation: str, context: Dict[str, Any]) -> bool:
        """Enforce policies on operation."""
        # Check all applicable policies
        for policy_id, policy in self._policies.items():
            if not policy.allows(operation, context):
                self._audit_log.append({
                    "operation": operation,
                    "policy": policy_id,
                    "result": "denied",
                    "context": context
                })
                logger.warning(f"Policy {policy_id} denied {operation}")
                return False

        # Log approval
        self._audit_log.append({
            "operation": operation,
            "result": "approved",
            "context": context
        })
        return True

    def get_audit_trail(self):
        """Get governance audit trail."""
        return self._audit_log.copy()

# Global policy integration
_policy_integration = None

def get_policy_integration():
    """Get global policy integration."""
    global _policy_integration
    if _policy_integration is None:
        _policy_integration = PolicyGovernanceIntegration()
    return _policy_integration
