"""
Policy Engine

Evaluates and enforces policies for prompt operations.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from hypersync.policy.budget.manager import get_budget_manager, BudgetAction


class PolicyVerb(Enum):
    """Policy verbs (actions)."""
    TOKEN_BUDGET = "token:budget"
    PROMPT_PREPROCESS = "prompt:preprocess"
    CLOUD_INVOKE = "cloud:invoke"
    PROVIDER_SELECT = "provider:select"


@dataclass
class PolicyContext:
    """Context for policy evaluation."""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    provider_id: Optional[str] = None
    tokens: int = 0
    cost_usd: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PolicyDecision:
    """Result of policy evaluation."""
    allowed: bool
    reason: Optional[str] = None
    action: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class PolicyEngine:
    """
    Evaluates policies and enforces rules.

    Integrates with:
    - Budget manager for token limits
    - Provider registry for routing
    - Telemetry for auditing
    """

    def __init__(self):
        self.budget_manager = get_budget_manager()
        self._policies: List[Dict] = []

    def load_policy(self, policy: Dict):
        """
        Load a policy.

        Args:
            policy: Policy configuration dict
        """
        self._policies.append(policy)

        # Load into budget manager if it's a budget policy
        if "token:budget" in policy.get("verbs", []):
            self.budget_manager.load_policy(policy)

    def load_policies_from_file(self, file_path: str):
        """Load policies from JSON file."""
        with open(file_path) as f:
            data = json.load(f)

        for policy in data.get("policies", []):
            self.load_policy(policy)

    def evaluate(
        self,
        verb: PolicyVerb,
        context: PolicyContext
    ) -> PolicyDecision:
        """
        Evaluate policies for an action.

        Args:
            verb: Action being performed
            context: Context for evaluation

        Returns:
            PolicyDecision with allow/deny and reason
        """
        # Find applicable policies
        applicable = self._find_applicable_policies(verb, context)

        if not applicable:
            # No policies, allow by default
            return PolicyDecision(allowed=True)

        # Sort by priority (highest first)
        applicable.sort(key=lambda p: p.get("priority", 0), reverse=True)

        # Evaluate each policy
        for policy in applicable:
            decision = self._evaluate_policy(policy, verb, context)

            if not decision.allowed:
                # Policy denied, return immediately
                return decision

        # All policies passed
        return PolicyDecision(allowed=True)

    def _find_applicable_policies(
        self,
        verb: PolicyVerb,
        context: PolicyContext
    ) -> List[Dict]:
        """Find policies that apply to this verb and context."""
        applicable = []

        for policy in self._policies:
            # Check if policy is enabled
            if not policy.get("enabled", True):
                continue

            # Check if verb matches
            if verb.value not in policy.get("verbs", []):
                continue

            # Check scope
            scope = policy.get("scope", {})

            # Check user scope
            if scope.get("users"):
                if context.user_id not in scope["users"]:
                    continue

            # Check provider scope
            if scope.get("providers"):
                if context.provider_id not in scope["providers"]:
                    continue

            # Check session scope
            if scope.get("sessions"):
                if context.session_id not in scope["sessions"]:
                    continue

            # Policy applies
            applicable.append(policy)

        return applicable

    def _evaluate_policy(
        self,
        policy: Dict,
        verb: PolicyVerb,
        context: PolicyContext
    ) -> PolicyDecision:
        """Evaluate a single policy."""
        if verb == PolicyVerb.TOKEN_BUDGET:
            return self._evaluate_budget_policy(policy, context)
        elif verb == PolicyVerb.PROMPT_PREPROCESS:
            return self._evaluate_preprocess_policy(policy, context)
        elif verb == PolicyVerb.CLOUD_INVOKE:
            return self._evaluate_cloud_invoke_policy(policy, context)
        else:
            # Unknown verb, allow
            return PolicyDecision(allowed=True)

    def _evaluate_budget_policy(
        self,
        policy: Dict,
        context: PolicyContext
    ) -> PolicyDecision:
        """Evaluate budget policy."""
        # Determine scope ID
        scope_id = self._get_scope_id(policy, context)

        # Check budget
        allowed, reason = self.budget_manager.check_budget(
            scope_id,
            context.tokens,
            context.cost_usd
        )

        if not allowed:
            # Get enforcement action
            enforcement = policy.get("enforcement", {})
            action = enforcement.get("action", "block")

            return PolicyDecision(
                allowed=False,
                reason=reason,
                action=action,
                metadata={
                    "policy_id": policy.get("policy_id"),
                    "scope_id": scope_id
                }
            )

        # Budget check passed
        return PolicyDecision(allowed=True)

    def _evaluate_preprocess_policy(
        self,
        policy: Dict,
        context: PolicyContext
    ) -> PolicyDecision:
        """Evaluate preprocessing requirement policy."""
        enforcement = policy.get("enforcement", {})
        require_preprocess = enforcement.get("require_preprocess", True)

        if require_preprocess:
            # Check if preprocessing was done
            if not context.metadata.get("preprocessed", False):
                return PolicyDecision(
                    allowed=False,
                    reason="Local preprocessing required by policy",
                    action="require_preprocess"
                )

        return PolicyDecision(allowed=True)

    def _evaluate_cloud_invoke_policy(
        self,
        policy: Dict,
        context: PolicyContext
    ) -> PolicyDecision:
        """Evaluate cloud invocation policy."""
        # For now, just check budget
        return self._evaluate_budget_policy(policy, context)

    def _get_scope_id(self, policy: Dict, context: PolicyContext) -> str:
        """Determine scope ID for budget tracking."""
        scope = policy.get("scope", {})

        # Prefer user scope
        if scope.get("users") and context.user_id:
            return f"user:{context.user_id}"

        # Then provider scope
        if scope.get("providers") and context.provider_id:
            return f"provider:{context.provider_id}"

        # Then session scope
        if scope.get("sessions") and context.session_id:
            return f"session:{context.session_id}"

        # Default to global
        return "global"

    def record_usage(self, context: PolicyContext):
        """Record token usage after successful request."""
        # Record for all applicable scopes
        if context.user_id:
            self.budget_manager.record_usage(
                f"user:{context.user_id}",
                context.tokens,
                context.cost_usd
            )

        if context.provider_id:
            self.budget_manager.record_usage(
                f"provider:{context.provider_id}",
                context.tokens,
                context.cost_usd
            )

        if context.session_id:
            self.budget_manager.record_usage(
                f"session:{context.session_id}",
                context.tokens,
                context.cost_usd
            )


# Global policy engine
_global_engine = None


def get_policy_engine() -> PolicyEngine:
    """Get the global policy engine."""
    global _global_engine
    if _global_engine is None:
        _global_engine = PolicyEngine()
    return _global_engine
