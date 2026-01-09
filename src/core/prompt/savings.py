"""
Savings Estimator

Calculates token and cost savings from compression pipeline.
"""

from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class SavingsEstimate:
    """Estimated savings from compression."""
    baseline_tokens: int
    compressed_tokens: int
    tokens_saved: int
    savings_percent: float
    baseline_cost_usd: float
    actual_cost_usd: float
    cost_saved_usd: float

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "baseline_tokens": self.baseline_tokens,
            "compressed_tokens": self.compressed_tokens,
            "tokens_saved": self.tokens_saved,
            "savings_percent": self.savings_percent,
            "baseline_cost_usd": self.baseline_cost_usd,
            "actual_cost_usd": self.actual_cost_usd,
            "cost_saved_usd": self.cost_saved_usd
        }


class SavingsEstimator:
    """
    Estimates token and cost savings.

    Compares baseline (no compression) vs. actual (with compression).
    """

    # Pricing per 1K tokens (approximate)
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
        "claude-3": {"input": 0.015, "output": 0.075},
        "claude-sonnet": {"input": 0.003, "output": 0.015}
    }

    def estimate(
        self,
        baseline_tokens: int,
        compressed_tokens: int,
        model: str = "gpt-4",
        output_tokens: int = 500
    ) -> SavingsEstimate:
        """
        Estimate savings.

        Args:
            baseline_tokens: Tokens without compression
            compressed_tokens: Tokens with compression
            model: Model being used
            output_tokens: Expected output tokens

        Returns:
            SavingsEstimate with detailed breakdown
        """
        # Calculate token savings
        tokens_saved = baseline_tokens - compressed_tokens
        savings_percent = (tokens_saved / baseline_tokens * 100) if baseline_tokens > 0 else 0

        # Get pricing
        pricing = self._get_pricing(model)

        # Calculate costs
        baseline_cost = (
            (baseline_tokens / 1000) * pricing["input"] +
            (output_tokens / 1000) * pricing["output"]
        )

        actual_cost = (
            (compressed_tokens / 1000) * pricing["input"] +
            (output_tokens / 1000) * pricing["output"]
        )

        cost_saved = baseline_cost - actual_cost

        return SavingsEstimate(
            baseline_tokens=baseline_tokens,
            compressed_tokens=compressed_tokens,
            tokens_saved=tokens_saved,
            savings_percent=round(savings_percent, 2),
            baseline_cost_usd=round(baseline_cost, 4),
            actual_cost_usd=round(actual_cost, 4),
            cost_saved_usd=round(cost_saved, 4)
        )

    def _get_pricing(self, model: str) -> Dict[str, float]:
        """Get pricing for a model."""
        # Try exact match
        if model in self.PRICING:
            return self.PRICING[model]

        # Try prefix match
        for key in self.PRICING:
            if model.startswith(key):
                return self.PRICING[key]

        # Default to GPT-4 pricing
        return self.PRICING["gpt-4"]

    def estimate_from_receipt(self, receipt: Dict) -> SavingsEstimate:
        """
        Estimate savings from a token receipt.

        Args:
            receipt: Token receipt dictionary

        Returns:
            SavingsEstimate
        """
        savings = receipt.get("savings", {})

        return SavingsEstimate(
            baseline_tokens=savings.get("baseline_tokens", 0),
            compressed_tokens=savings.get("actual_tokens", 0),
            tokens_saved=savings.get("tokens_saved", 0),
            savings_percent=savings.get("savings_percent", 0),
            baseline_cost_usd=0.0,  # TODO: Calculate from receipt
            actual_cost_usd=receipt.get("provider", {}).get("cost_usd", 0.0),
            cost_saved_usd=savings.get("cost_saved_usd", 0.0)
        )


# Global estimator instance
_global_estimator = None


def get_estimator() -> SavingsEstimator:
    """Get the global savings estimator."""
    global _global_estimator
    if _global_estimator is None:
        _global_estimator = SavingsEstimator()
    return _global_estimator
