"""
Token Statistics Module

Aggregates and queries token usage statistics.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from hypersync.token.receipts import get_accumulator, TokenReceipt


@dataclass
class TokenStats:
    """Token usage statistics."""
    total_tokens: int
    tokens_saved: int
    request_count: int
    average_tokens_per_request: float
    average_savings_percent: float
    total_cost_usd: float
    cost_saved_usd: float

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "total_tokens": self.total_tokens,
            "tokens_saved": self.tokens_saved,
            "request_count": self.request_count,
            "average_tokens_per_request": self.average_tokens_per_request,
            "average_savings_percent": self.average_savings_percent,
            "total_cost_usd": self.total_cost_usd,
            "cost_saved_usd": self.cost_saved_usd
        }


class TokenStatsAggregator:
    """
    Aggregates token statistics from receipts.

    Provides various views:
    - By time period (today, week, month)
    - By user
    - By provider
    - By session
    """

    def __init__(self):
        self.accumulator = get_accumulator()

    def get_stats(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        provider: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> TokenStats:
        """
        Get aggregated statistics.

        Args:
            user_id: Filter by user
            session_id: Filter by session
            provider: Filter by provider
            start_date: Start of time range
            end_date: End of time range

        Returns:
            TokenStats with aggregated data
        """
        # Get receipts
        receipts = self.accumulator.list_receipts(
            user_id=user_id,
            session_id=session_id
        )

        # Filter by date
        if start_date or end_date:
            receipts = self._filter_by_date(receipts, start_date, end_date)

        # Filter by provider
        if provider:
            receipts = [
                r for r in receipts
                if r.provider and r.provider.get("provider_id") == provider
            ]

        # Aggregate
        return self._aggregate(receipts)

    def get_today_stats(
        self,
        user_id: Optional[str] = None,
        provider: Optional[str] = None
    ) -> TokenStats:
        """Get statistics for today."""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.get_stats(
            user_id=user_id,
            provider=provider,
            start_date=today
        )

    def get_week_stats(
        self,
        user_id: Optional[str] = None,
        provider: Optional[str] = None
    ) -> TokenStats:
        """Get statistics for the past week."""
        week_ago = datetime.utcnow() - timedelta(days=7)
        return self.get_stats(
            user_id=user_id,
            provider=provider,
            start_date=week_ago
        )

    def get_month_stats(
        self,
        user_id: Optional[str] = None,
        provider: Optional[str] = None
    ) -> TokenStats:
        """Get statistics for the past month."""
        month_ago = datetime.utcnow() - timedelta(days=30)
        return self.get_stats(
            user_id=user_id,
            provider=provider,
            start_date=month_ago
        )

    def get_by_provider(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, TokenStats]:
        """
        Get statistics grouped by provider.

        Returns:
            Dict mapping provider ID to TokenStats
        """
        receipts = self.accumulator.list_receipts(user_id=user_id)

        if start_date or end_date:
            receipts = self._filter_by_date(receipts, start_date, end_date)

        # Group by provider
        by_provider = {}
        for receipt in receipts:
            if not receipt.provider:
                continue

            provider_id = receipt.provider.get("provider_id", "unknown")

            if provider_id not in by_provider:
                by_provider[provider_id] = []

            by_provider[provider_id].append(receipt)

        # Aggregate each group
        return {
            provider_id: self._aggregate(receipts)
            for provider_id, receipts in by_provider.items()
        }

    def get_by_user(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, TokenStats]:
        """
        Get statistics grouped by user.

        Returns:
            Dict mapping user ID to TokenStats
        """
        receipts = self.accumulator.list_receipts()

        if start_date or end_date:
            receipts = self._filter_by_date(receipts, start_date, end_date)

        # Group by user
        by_user = {}
        for receipt in receipts:
            if not receipt.user_id:
                continue

            if receipt.user_id not in by_user:
                by_user[receipt.user_id] = []

            by_user[receipt.user_id].append(receipt)

        # Aggregate each group
        return {
            user_id: self._aggregate(receipts)
            for user_id, receipts in by_user.items()
        }

    def _filter_by_date(
        self,
        receipts: List[TokenReceipt],
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> List[TokenReceipt]:
        """Filter receipts by date range."""
        filtered = receipts

        if start_date:
            filtered = [
                r for r in filtered
                if datetime.fromisoformat(r.timestamp.rstrip('Z')) >= start_date
            ]

        if end_date:
            filtered = [
                r for r in filtered
                if datetime.fromisoformat(r.timestamp.rstrip('Z')) <= end_date
            ]

        return filtered

    def _aggregate(self, receipts: List[TokenReceipt]) -> TokenStats:
        """Aggregate statistics from receipts."""
        if not receipts:
            return TokenStats(
                total_tokens=0,
                tokens_saved=0,
                request_count=0,
                average_tokens_per_request=0.0,
                average_savings_percent=0.0,
                total_cost_usd=0.0,
                cost_saved_usd=0.0
            )

        total_tokens = sum(
            r.total_tokens.get("provider_charged", 0)
            for r in receipts
        )

        tokens_saved = sum(
            r.total_tokens.get("saved", 0)
            for r in receipts
        )

        request_count = len(receipts)

        average_tokens = total_tokens / request_count if request_count > 0 else 0

        # Average savings percent
        savings_percents = [
            r.savings.get("savings_percent", 0)
            for r in receipts
            if r.savings
        ]
        average_savings = sum(savings_percents) / len(savings_percents) if savings_percents else 0

        # Total cost
        total_cost = sum(
            r.provider.get("cost_usd", 0)
            for r in receipts
            if r.provider
        )

        # Cost saved
        cost_saved = sum(
            r.savings.get("cost_saved_usd", 0)
            for r in receipts
            if r.savings
        )

        return TokenStats(
            total_tokens=total_tokens,
            tokens_saved=tokens_saved,
            request_count=request_count,
            average_tokens_per_request=round(average_tokens, 2),
            average_savings_percent=round(average_savings, 2),
            total_cost_usd=round(total_cost, 4),
            cost_saved_usd=round(cost_saved, 4)
        )


# Global aggregator instance
_global_aggregator = None


def get_stats_aggregator() -> TokenStatsAggregator:
    """Get the global stats aggregator."""
    global _global_aggregator
    if _global_aggregator is None:
        _global_aggregator = TokenStatsAggregator()
    return _global_aggregator
