"""
HyperSync Clearance Enforcement Module

Integrates clearance checking into agent request flow.
"""

from typing import Dict, Optional, Any
from hypersync.security.policy.agent_policy_manager import (
    AgentPolicyManager, ClearanceLevel, PrincipalType
)
import logging

logger = logging.getLogger(__name__)


class ClearanceEnforcer:
    """
    Enforces clearance-based access control for agent requests.

    Integrates with policy manager to validate clearances and
    determine redaction requirements.
    """

    def __init__(self, policy_manager: AgentPolicyManager):
        """
        Initialize clearance enforcer.

        Args:
            policy_manager: Agent policy manager instance
        """
        self.policy_manager = policy_manager

    def check_request_clearance(self, agent_id: str, requester_id: str,
                                agent_profile: Dict, action: str) -> Dict[str, Any]:
        """
        Check if a request meets clearance requirements.

        Args:
            agent_id: Agent identifier
            requester_id: Original requester identifier
            agent_profile: Agent profile with policy bindings
            action: Action being requested

        Returns:
            Clearance check result with decision and redaction requirements
        """
        # Extract clearances
        agent_clearance_str = agent_profile.get('policy_bindings', {}).get(
            'clearance_level', 'internal'
        )

        # Build context
        context = {
            'agent_id': agent_id,
            'requester': requester_id,
            'agent_clearance': agent_clearance_str
        }

        # Build prompt request (minimal for policy evaluation)
        prompt_request = {
            'action': action,
            'agent_id': agent_id,
            'requester_id': requester_id
        }

        # Evaluate policy
        decision = self.policy_manager.evaluate(action, prompt_request, context)

        # Determine redaction requirements
        clearance_context = decision.get('clearance_context', {})
        requires_redaction = clearance_context.get('is_escalation', False)

        result = {
            'allowed': decision['decision'] == self.policy_manager.EFFECT_ALLOW,
            'decision': decision['decision'].value,
            'requires_redaction': requires_redaction,
            'agent_clearance': clearance_context.get('agent_clearance'),
            'requester_clearance': clearance_context.get('requester_clearance'),
            'is_escalation': clearance_context.get('is_escalation', False),
            'deny_reason': decision.get('deny_reason'),
            'matched_policies': decision.get('matched_policies', [])
        }

        if not result['allowed']:
            logger.warning(
                f"Clearance check failed for agent {agent_id}, "
                f"requester {requester_id}: {result['deny_reason']}"
            )

        return result

    def validate_delegation_chain(self, delegation_chain: list,
                                  requester_clearance: str) -> Dict[str, Any]:
        """
        Validate a delegation chain respects clearance constraints.

        Args:
            delegation_chain: List of agent IDs in delegation order
            requester_clearance: Original requester's clearance

        Returns:
            Validation result
        """
        req_level = ClearanceLevel.from_string(requester_clearance)

        violations = []
        max_clearance = req_level

        for i, agent_id in enumerate(delegation_chain):
            # TODO: Look up agent clearance from registry
            # For now, assume internal
            agent_clearance = ClearanceLevel.INTERNAL

            if agent_clearance > max_clearance:
                max_clearance = agent_clearance

            # Check if escalation is allowed
            if agent_clearance > req_level:
                violations.append({
                    'agent_id': agent_id,
                    'position': i,
                    'issue': 'clearance_escalation',
                    'agent_clearance': agent_clearance.name,
                    'requester_clearance': req_level.name
                })

        return {
            'valid': len(violations) == 0,
            'violations': violations,
            'max_clearance': max_clearance.name,
            'requires_redaction': max_clearance > req_level
        }

    def get_redaction_requirements(self, agent_clearance: str,
                                   requester_clearance: str) -> Dict[str, Any]:
        """
        Determine redaction requirements for a request.

        Args:
            agent_clearance: Agent's clearance level
            requester_clearance: Requester's clearance level

        Returns:
            Redaction requirements
        """
        agent_level = ClearanceLevel.from_string(agent_clearance)
        req_level = ClearanceLevel.from_string(requester_clearance)

        is_escalation = agent_level > req_level

        return {
            'required': is_escalation,
            'target_level': req_level.name.lower(),
            'source_level': agent_level.name.lower(),
            'redaction_profile': self._get_redaction_profile(req_level),
            'filters': self._get_redaction_filters(agent_level, req_level)
        }

    def _get_redaction_profile(self, clearance: ClearanceLevel) -> str:
        """Get redaction profile name for clearance level."""
        profiles = {
            ClearanceLevel.PUBLIC: 'public-safe',
            ClearanceLevel.INTERNAL: 'internal-standard',
            ClearanceLevel.RESTRICTED: 'restricted-moderate',
            ClearanceLevel.CONFIDENTIAL: 'confidential-strict',
            ClearanceLevel.SECRET: 'secret-minimal'
        }
        return profiles.get(clearance, 'default')

    def _get_redaction_filters(self, source: ClearanceLevel, 
                              target: ClearanceLevel) -> list:
        """Get list of redaction filters to apply."""
        filters = []

        # Always apply PII filter
        filters.append('pii')

        # Add classification-based filters
        if target <= ClearanceLevel.PUBLIC:
            filters.extend(['internal-refs', 'confidential-data', 'secrets'])
        elif target <= ClearanceLevel.INTERNAL:
            filters.extend(['confidential-data', 'secrets'])
        elif target <= ClearanceLevel.RESTRICTED:
            filters.extend(['secrets'])

        return filters


class AgentAuthorizationError(Exception):
    """Raised when agent authorization fails."""

    def __init__(self, message: str, clearance_context: Optional[Dict] = None):
        super().__init__(message)
        self.clearance_context = clearance_context or {}


def enforce_clearance(policy_manager: AgentPolicyManager, agent_id: str,
                     requester_id: str, agent_profile: Dict, 
                     action: str) -> Dict[str, Any]:
    """
    Convenience function to enforce clearance for a request.

    Args:
        policy_manager: Policy manager instance
        agent_id: Agent identifier
        requester_id: Requester identifier
        agent_profile: Agent profile
        action: Action being requested

    Returns:
        Clearance check result

    Raises:
        AgentAuthorizationError: If clearance check fails
    """
    enforcer = ClearanceEnforcer(policy_manager)
    result = enforcer.check_request_clearance(
        agent_id, requester_id, agent_profile, action
    )

    if not result['allowed']:
        raise AgentAuthorizationError(
            result['deny_reason'],
            clearance_context=result
        )

    return result
