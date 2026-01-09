"""
Budget Manager

Tracks and enforces token budget limits.
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class BudgetAction(Enum):
    """Actions when budget limit is exceeded."""
    BLOCK = "block"
    WARN = "warn"
    THROTTLE = "throttle"
    REROUTE = "reroute"


@dataclass
class BudgetLimit:
    """Budget limit configuration."""
    daily_tokens: Optional[int] = None
    monthly_tokens: Optional[int] = None
    per_request_tokens: Optional[int] = None
    daily_cost_usd: Optional[float] = None
    monthly_cost_usd: Optional[float] = None


@dataclass
class BudgetUsage:
    """Current budget usage."""
    daily_tokens: int = 0
    monthly_tokens: int = 0
    daily_cost_usd: float = 0.0
    monthly_cost_usd: float = 0.0
    last_reset_daily: Optional[datetime] = None
    last_reset_monthly: Optional[datetime] = None


class BudgetManager:
    """
    Manages token budgets and enforces limits.

    Tracks usage per user, provider, and session.
    Enforces limits with configurable actions.
    """

    def __init__(self):
        self._limits: Dict[str, BudgetLimit] = {}
        self._usage: Dict[str, BudgetUsage] = {}
        self._policies: List[Dict] = []

    def set_limit(
        self,
        scope_id: str,
        limit: BudgetLimit
    ):
        """
        Set budget limit for a scope.

        Args:
            scope_id: Scope identifier (user_id, provider_id, etc.)
            limit: Budget limit configuration
        """
        self._limits[scope_id] = limit

        # Initialize usage if not exists
        if scope_id not in self._usage:
            self._usage[scope_id] = BudgetUsage(
                last_reset_daily=datetime.utcnow(),
                last_reset_monthly=datetime.utcnow()
            )

    def check_budget(
        self,
        scope_id: str,
        tokens: int,
        cost_usd: float = 0.0
    ) -> tuple[bool, Optional[str]]:
        """
        Check if request is within budget.

        Args:
            scope_id: Scope identifier
            tokens: Tokens for this request
            cost_usd: Cost for this request

        Returns:
            (allowed, reason) tuple
        """
        # Reset usage if needed
        self._reset_usage_if_needed(scope_id)

        # Get limit and usage
        limit = self._limits.get(scope_id)
        if not limit:
            # No limit set, allow
            return True, None

        usage = self._usage.get(scope_id)
        if not usage:
            # No usage tracked, allow
            return True, None

        # Check per-request limit
        if limit.per_request_tokens and tokens > limit.per_request_tokens:
            return False, f"Request exceeds per-request limit ({tokens} > {limit.per_request_tokens})"

        # Check daily token limit
        if limit.daily_tokens and (usage.daily_tokens + tokens) > limit.daily_tokens:
            return False, f"Daily token limit exceeded ({usage.daily_tokens + tokens} > {limit.daily_tokens})"

        # Check monthly token limit
        if limit.monthly_tokens and (usage.monthly_tokens + tokens) > limit.monthly_tokens:
            return False, f"Monthly token limit exceeded ({usage.monthly_tokens + tokens} > {limit.monthly_tokens})"

        # Check daily cost limit
        if limit.daily_cost_usd and (usage.daily_cost_usd + cost_usd) > limit.daily_cost_usd:
            return False, f"Daily cost limit exceeded (${usage.daily_cost_usd + cost_usd:.2f} > ${limit.daily_cost_usd:.2f})"

        # Check monthly cost limit
        if limit.monthly_cost_usd and (usage.monthly_cost_usd + cost_usd) > limit.monthly_cost_usd:
            return False, f"Monthly cost limit exceeded (${usage.monthly_cost_usd + cost_usd:.2f} > ${limit.monthly_cost_usd:.2f})"

        # All checks passed
        return True, None

    def record_usage(
        self,
        scope_id: str,
        tokens: int,
        cost_usd: float = 0.0
    ):
        """
        Record token usage.

        Args:
            scope_id: Scope identifier
            tokens: Tokens used
            cost_usd: Cost incurred
        """
        # Reset usage if needed
        self._reset_usage_if_needed(scope_id)

        # Get or create usage
        if scope_id not in self._usage:
            self._usage[scope_id] = BudgetUsage(
                last_reset_daily=datetime.utcnow(),
                last_reset_monthly=datetime.utcnow()
            )

        usage = self._usage[scope_id]

        # Update usage
        usage.daily_tokens += tokens
        usage.monthly_tokens += tokens
        usage.daily_cost_usd += cost_usd
        usage.monthly_cost_usd += cost_usd

    def get_usage(self, scope_id: str) -> Optional[BudgetUsage]:
        """Get current usage for a scope."""
        self._reset_usage_if_needed(scope_id)
        return self._usage.get(scope_id)

    def get_remaining(
        self,
        scope_id: str
    ) -> Dict[str, int]:
        """
        Get remaining budget.

        Returns:
            Dict with remaining tokens and cost
        """
        limit = self._limits.get(scope_id)
        usage = self.get_usage(scope_id)

        if not limit or not usage:
            return {
                "daily_tokens": float('inf'),
                "monthly_tokens": float('inf'),
                "daily_cost_usd": float('inf'),
                "monthly_cost_usd": float('inf')
            }

        return {
            "daily_tokens": limit.daily_tokens - usage.daily_tokens if limit.daily_tokens else float('inf'),
            "monthly_tokens": limit.monthly_tokens - usage.monthly_tokens if limit.monthly_tokens else float('inf'),
            "daily_cost_usd": limit.daily_cost_usd - usage.daily_cost_usd if limit.daily_cost_usd else float('inf'),
            "monthly_cost_usd": limit.monthly_cost_usd - usage.monthly_cost_usd if limit.monthly_cost_usd else float('inf')
        }

    def _reset_usage_if_needed(self, scope_id: str):
        """Reset usage counters if period has elapsed."""
        usage = self._usage.get(scope_id)
        if not usage:
            return

        now = datetime.utcnow()

        # Reset daily if needed
        if usage.last_reset_daily:
            if (now - usage.last_reset_daily) >= timedelta(days=1):
                usage.daily_tokens = 0
                usage.daily_cost_usd = 0.0
                usage.last_reset_daily = now

        # Reset monthly if needed
        if usage.last_reset_monthly:
            if (now - usage.last_reset_monthly) >= timedelta(days=30):
                usage.monthly_tokens = 0
                usage.monthly_cost_usd = 0.0
                usage.last_reset_monthly = now

    def load_policy(self, policy: Dict):
        """Load a budget policy."""
        self._policies.append(policy)

        # Extract limits
        limits_data = policy.get("limits", {})
        limit = BudgetLimit(
            daily_tokens=limits_data.get("daily_tokens"),
            monthly_tokens=limits_data.get("monthly_tokens"),
            per_request_tokens=limits_data.get("per_request_tokens"),
            daily_cost_usd=limits_data.get("daily_cost_usd"),
            monthly_cost_usd=limits_data.get("monthly_cost_usd")
        )

        # Apply to scopes
        scope = policy.get("scope", {})

        # Apply to users
        for user_id in scope.get("users", []):
            self.set_limit(f"user:{user_id}", limit)

        # Apply to providers
        for provider_id in scope.get("providers", []):
            self.set_limit(f"provider:{provider_id}", limit)


# Global budget manager
_global_manager = None


def get_budget_manager() -> BudgetManager:
    """Get the global budget manager."""
    global _global_manager
    if _global_manager is None:
        _global_manager = BudgetManager()
    return _global_manager
