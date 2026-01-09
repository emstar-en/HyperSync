"""Budget Enforcer - Enforce token budgets."""
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class BudgetExceededError(Exception):
    """Raised when budget is exceeded."""
    pass


class BudgetEnforcer:
    """Enforce token budgets."""

    def __init__(self):
        self._budgets: Dict[str, Dict] = {}
        self._usage: Dict[str, int] = {}

    def set_budget(
        self,
        user_id: str,
        budget_tokens: int,
        period: str = "daily"
    ):
        """Set budget for user."""
        self._budgets[user_id] = {
            "tokens": budget_tokens,
            "period": period,
            "set_at": datetime.now()
        }
        logger.info(f"Set budget for {user_id}: {budget_tokens} tokens/{period}")

    def can_consume(self, user_id: str, estimated_tokens: int) -> bool:
        """Check if user can consume tokens."""
        if user_id not in self._budgets:
            return True  # No budget set

        budget = self._budgets[user_id]
        current_usage = self._usage.get(user_id, 0)

        return (current_usage + estimated_tokens) <= budget["tokens"]

    def consume(self, user_id: str, actual_tokens: int):
        """Consume tokens from budget."""
        if not self.can_consume(user_id, actual_tokens):
            raise BudgetExceededError(f"Budget exceeded for {user_id}")

        self._usage[user_id] = self._usage.get(user_id, 0) + actual_tokens
        logger.debug(f"Consumed {actual_tokens} tokens for {user_id}")

    def get_remaining(self, user_id: str) -> Optional[int]:
        """Get remaining budget."""
        if user_id not in self._budgets:
            return None

        budget = self._budgets[user_id]["tokens"]
        used = self._usage.get(user_id, 0)
        return max(0, budget - used)


_budget_enforcer: Optional[BudgetEnforcer] = None


def get_budget_enforcer() -> BudgetEnforcer:
    """Get global budget enforcer."""
    global _budget_enforcer
    if _budget_enforcer is None:
        _budget_enforcer = BudgetEnforcer()
    return _budget_enforcer
