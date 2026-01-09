"""
HyperSync Agent-Aware Policy Manager Extension

Extends the existing policy manager to recognize agent principals and
enforce clearance-based access control with delegation support.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PrincipalType(Enum):
    """Principal types for policy evaluation."""
    USER = "user"
    AGENT = "agent"
    SERVICE = "service"
    SYSTEM = "system"


class ClearanceLevel(Enum):
    """Security clearance levels (ordered lowest to highest)."""
    PUBLIC = 0
    INTERNAL = 1
    RESTRICTED = 2
    CONFIDENTIAL = 3
    SECRET = 4

    @classmethod
    def from_string(cls, level: str) -> 'ClearanceLevel':
        """Convert string to clearance level."""
        return cls[level.upper()]

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value


class PolicyEffect(Enum):
    """Policy decision effects."""
    ALLOW = "allow"
    DENY = "deny"


class AgentPolicyManager:
    """
    Extended policy manager with agent-aware evaluation.

    Supports:
    - Agent principal recognition
    - Clearance level enforcement
    - Delegation chain validation
    - Requester context propagation
    """

    EFFECT_ALLOW = PolicyEffect.ALLOW
    EFFECT_DENY = PolicyEffect.DENY

    def __init__(self, policy_store: Optional[Any] = None):
        """
        Initialize agent policy manager.

        Args:
            policy_store: Optional policy storage backend
        """
        self.policy_store = policy_store
        self.policies: Dict[str, Dict] = {}
        self.clearance_hierarchy = self._build_default_hierarchy()

    def _build_default_hierarchy(self) -> Dict[str, List[str]]:
        """Build default clearance level hierarchy."""
        return {
            'public': [],
            'internal': ['public'],
            'restricted': ['public', 'internal'],
            'confidential': ['public', 'internal', 'restricted'],
            'secret': ['public', 'internal', 'restricted', 'confidential']
        }

    def load_policy(self, policy: Dict) -> None:
        """
        Load a policy into the manager.

        Args:
            policy: Policy definition dictionary
        """
        policy_id = policy['policy_id']
        self.policies[policy_id] = policy
        logger.info(f"Loaded policy: {policy_id}")

    def evaluate(self, action: str, prompt_request: Dict, 
                 context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Evaluate a policy decision for an action.

        Args:
            action: Action being requested (e.g., "prompt:invoke")
            prompt_request: Request packet with prompt details
            context: Additional context (agent_id, requester, etc.)

        Returns:
            Decision dictionary with effect, reason, and metadata
        """
        context = context or {}

        # Extract principal information
        principal = self._extract_principal(prompt_request, context)

        # Determine if this is an agent-mediated request
        is_agent_request = principal['type'] == PrincipalType.AGENT

        # Get requester clearance (original user if agent-mediated)
        requester_clearance = self._get_requester_clearance(principal, context)

        # Get agent clearance (if applicable)
        agent_clearance = self._get_agent_clearance(context) if is_agent_request else None

        # Evaluate all applicable policies
        decisions = []
        for policy_id, policy in self.policies.items():
            decision = self._evaluate_policy(
                policy, action, principal, requester_clearance, 
                agent_clearance, context
            )
            if decision:
                decisions.append(decision)

        # Combine decisions (deny takes precedence)
        final_decision = self._combine_decisions(decisions)

        # Add clearance context
        final_decision['clearance_context'] = {
            'requester_clearance': requester_clearance.name if requester_clearance else None,
            'agent_clearance': agent_clearance.name if agent_clearance else None,
            'is_escalation': (
                agent_clearance and requester_clearance and 
                agent_clearance > requester_clearance
            ) if agent_clearance and requester_clearance else False
        }

        logger.info(f"Policy decision for {action}: {final_decision['decision'].value}")
        return final_decision

    def _extract_principal(self, prompt_request: Dict, context: Dict) -> Dict:
        """Extract principal information from request and context."""
        if 'agent_id' in context:
            return {
                'type': PrincipalType.AGENT,
                'id': context['agent_id'],
                'requester_id': context.get('requester')
            }
        elif 'user_id' in context:
            return {
                'type': PrincipalType.USER,
                'id': context['user_id']
            }
        elif 'service_id' in context:
            return {
                'type': PrincipalType.SERVICE,
                'id': context['service_id']
            }
        else:
            return {
                'type': PrincipalType.SYSTEM,
                'id': 'system'
            }

    def _get_requester_clearance(self, principal: Dict, context: Dict) -> Optional[ClearanceLevel]:
        """Get clearance level of the original requester."""
        if principal['type'] == PrincipalType.AGENT:
            # For agent requests, get the original user's clearance
            requester_id = principal.get('requester_id')
            if requester_id:
                return self._lookup_user_clearance(requester_id)
        else:
            # Direct user request
            return self._lookup_user_clearance(principal['id'])

        return ClearanceLevel.PUBLIC  # Default

    def _get_agent_clearance(self, context: Dict) -> Optional[ClearanceLevel]:
        """Get clearance level of the agent."""
        agent_id = context.get('agent_id')
        if not agent_id:
            return None

        # Look up agent's configured clearance
        agent_clearance_str = context.get('agent_clearance', 'internal')
        return ClearanceLevel.from_string(agent_clearance_str)

    def _lookup_user_clearance(self, user_id: str) -> ClearanceLevel:
        """Look up user's clearance level (stub - integrate with user directory)."""
        # TODO: Integrate with actual user directory
        # For now, return default based on user_id pattern
        if 'admin' in user_id:
            return ClearanceLevel.SECRET
        elif 'internal' in user_id:
            return ClearanceLevel.INTERNAL
        else:
            return ClearanceLevel.PUBLIC

    def _evaluate_policy(self, policy: Dict, action: str, principal: Dict,
                        requester_clearance: Optional[ClearanceLevel],
                        agent_clearance: Optional[ClearanceLevel],
                        context: Dict) -> Optional[Dict]:
        """Evaluate a single policy against the request."""
        for rule in policy.get('rules', []):
            if self._rule_matches(rule, action, principal, requester_clearance, 
                                 agent_clearance, context):
                return {
                    'decision': PolicyEffect[rule['effect'].upper()],
                    'policy_id': policy['policy_id'],
                    'rule_id': rule['rule_id'],
                    'reason': f"Matched rule {rule['rule_id']} in policy {policy['policy_id']}"
                }

        return None

    def _rule_matches(self, rule: Dict, action: str, principal: Dict,
                     requester_clearance: Optional[ClearanceLevel],
                     agent_clearance: Optional[ClearanceLevel],
                     context: Dict) -> bool:
        """Check if a rule matches the request."""
        # Check action
        if action not in rule.get('actions', []):
            return False

        # Check principal type
        principals_config = rule.get('principals', {})
        allowed_types = principals_config.get('types', [])
        if allowed_types and principal['type'].value not in allowed_types:
            return False

        # Check principal IDs
        allowed_ids = principals_config.get('ids', [])
        if allowed_ids and principal['id'] not in allowed_ids:
            return False

        # Check clearance levels
        allowed_clearances = principals_config.get('clearance_levels', [])
        if allowed_clearances:
            # For agent requests, check both requester and agent clearance
            if principal['type'] == PrincipalType.AGENT:
                if agent_clearance:
                    agent_clearance_str = agent_clearance.name.lower()
                    if agent_clearance_str not in allowed_clearances:
                        return False
            else:
                if requester_clearance:
                    requester_clearance_str = requester_clearance.name.lower()
                    if requester_clearance_str not in allowed_clearances:
                        return False

        # Check conditions
        conditions = rule.get('conditions', {})

        # Check clearance escalation
        if 'clearance_escalation' in conditions:
            allow_escalation = conditions['clearance_escalation']
            is_escalation = (
                agent_clearance and requester_clearance and 
                agent_clearance > requester_clearance
            )
            if is_escalation and not allow_escalation:
                return False

        # Check delegation depth
        if 'max_delegation_depth' in conditions:
            max_depth = conditions['max_delegation_depth']
            current_depth = context.get('delegation_depth', 0)
            if current_depth > max_depth:
                return False

        return True

    def _combine_decisions(self, decisions: List[Dict]) -> Dict[str, Any]:
        """Combine multiple policy decisions (deny takes precedence)."""
        if not decisions:
            # Default deny if no policies match
            return {
                'decision': self.EFFECT_DENY,
                'deny_reason': 'No matching policy found',
                'matched_policies': []
            }

        # Check for any denies
        for decision in decisions:
            if decision['decision'] == self.EFFECT_DENY:
                return {
                    'decision': self.EFFECT_DENY,
                    'deny_reason': decision['reason'],
                    'matched_policies': [d['policy_id'] for d in decisions]
                }

        # All allows
        return {
            'decision': self.EFFECT_ALLOW,
            'matched_policies': [d['policy_id'] for d in decisions]
        }

    def check_clearance_escalation(self, requester_clearance: str, 
                                   agent_clearance: str) -> Dict[str, Any]:
        """
        Check if an agent can escalate requester's clearance.

        Args:
            requester_clearance: Requester's clearance level
            agent_clearance: Agent's clearance level

        Returns:
            Escalation check result
        """
        req_level = ClearanceLevel.from_string(requester_clearance)
        agent_level = ClearanceLevel.from_string(agent_clearance)

        is_escalation = agent_level > req_level

        return {
            'is_escalation': is_escalation,
            'requester_level': req_level.name,
            'agent_level': agent_level.name,
            'allowed': is_escalation,  # TODO: Check policy
            'requires_redaction': is_escalation
        }

    def get_effective_clearance(self, requester_clearance: str,
                               agent_clearance: Optional[str] = None) -> str:
        """
        Get effective clearance for a request.

        Args:
            requester_clearance: Requester's clearance
            agent_clearance: Optional agent clearance

        Returns:
            Effective clearance level
        """
        if not agent_clearance:
            return requester_clearance

        req_level = ClearanceLevel.from_string(requester_clearance)
        agent_level = ClearanceLevel.from_string(agent_clearance)

        # Agent can access up to its clearance, but output must be
        # redacted to requester's level
        return agent_level.name.lower()

    def validate_policy(self, policy: Dict) -> Dict[str, Any]:
        """
        Validate a policy definition.

        Args:
            policy: Policy dictionary

        Returns:
            Validation result
        """
        errors = []

        # Check required fields
        if 'policy_id' not in policy:
            errors.append("Missing required field: policy_id")
        if 'version' not in policy:
            errors.append("Missing required field: version")
        if 'rules' not in policy:
            errors.append("Missing required field: rules")

        # Validate rules
        for i, rule in enumerate(policy.get('rules', [])):
            if 'rule_id' not in rule:
                errors.append(f"Rule {i}: Missing rule_id")
            if 'effect' not in rule or rule['effect'] not in ['allow', 'deny']:
                errors.append(f"Rule {i}: Invalid effect")
            if 'principals' not in rule:
                errors.append(f"Rule {i}: Missing principals")
            if 'actions' not in rule:
                errors.append(f"Rule {i}: Missing actions")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
