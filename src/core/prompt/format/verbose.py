"""
Verbose Response Formatter

Formats prompt responses with detailed token breakdowns.
"""

from typing import Dict, Any, Optional
from datetime import datetime


class VerboseFormatter:
    """
    Formats responses with verbose token information.

    Provides human-readable breakdowns of:
    - Per-stage token counts
    - Compression ratios
    - Cost estimates
    - Latency metrics
    """

    def format_response(
        self,
        response: Dict[str, Any],
        verbose: bool = False
    ) -> str:
        """
        Format a response for display.

        Args:
            response: Provider response with receipt
            verbose: Enable verbose formatting

        Returns:
            Formatted string
        """
        if not verbose:
            # Simple format: just the text
            return response.get("text", "")

        # Verbose format: text + token breakdown
        output = []

        # Response text
        output.append("=" * 80)
        output.append("RESPONSE")
        output.append("=" * 80)
        output.append(response.get("text", ""))
        output.append("")

        # Token breakdown
        receipt = response.get("receipt")
        if receipt:
            output.append("=" * 80)
            output.append("TOKEN BREAKDOWN")
            output.append("=" * 80)
            output.append(self._format_token_breakdown(receipt))
            output.append("")

        # Metadata
        metadata = response.get("metadata", {})
        if metadata:
            output.append("=" * 80)
            output.append("METADATA")
            output.append("=" * 80)
            output.append(self._format_metadata(metadata))

        return "
".join(output)

    def _format_token_breakdown(self, receipt: Dict) -> str:
        """Format token breakdown from receipt."""
        lines = []

        # Total tokens
        total = receipt.get("total_tokens", {})
        lines.append(f"Total Input Tokens:    {total.get('input', 0):,}")
        lines.append(f"Total Output Tokens:   {total.get('output', 0):,}")
        lines.append(f"Tokens Saved:          {total.get('saved', 0):,}")
        lines.append(f"Provider Charged:      {total.get('provider_charged', 0):,}")
        lines.append("")

        # Per-stage breakdown
        stages = receipt.get("stages", [])
        if stages:
            lines.append("Per-Stage Breakdown:")
            lines.append("-" * 80)

            for stage in stages:
                stage_name = stage.get("stage", "unknown")
                tokens_in = stage.get("tokens_in", 0)
                tokens_out = stage.get("tokens_out", 0)
                tokens_saved = stage.get("tokens_saved", 0)
                ratio = stage.get("compression_ratio", 1.0)
                latency = stage.get("latency_ms", 0)

                lines.append(f"  {stage_name:25} | In: {tokens_in:6,} | Out: {tokens_out:6,} | Saved: {tokens_saved:6,} | Ratio: {ratio:.2f} | {latency}ms")

            lines.append("")

        # Savings analysis
        savings = receipt.get("savings", {})
        if savings:
            lines.append("Savings Analysis:")
            lines.append("-" * 80)
            lines.append(f"Baseline Tokens:       {savings.get('baseline_tokens', 0):,}")
            lines.append(f"Actual Tokens:         {savings.get('actual_tokens', 0):,}")
            lines.append(f"Tokens Saved:          {savings.get('tokens_saved', 0):,}")
            lines.append(f"Savings Percent:       {savings.get('savings_percent', 0):.1f}%")

            cost_saved = savings.get('cost_saved_usd', 0)
            if cost_saved > 0:
                lines.append(f"Cost Saved:            ${cost_saved:.4f}")

            lines.append("")

        # Provider info
        provider = receipt.get("provider", {})
        if provider:
            lines.append("Provider Details:")
            lines.append("-" * 80)
            lines.append(f"Provider:              {provider.get('provider_id', 'unknown')}")
            lines.append(f"Model:                 {provider.get('model', 'unknown')}")
            lines.append(f"Prompt Tokens:         {provider.get('prompt_tokens', 0):,}")
            lines.append(f"Completion Tokens:     {provider.get('completion_tokens', 0):,}")

            cost = provider.get('cost_usd', 0)
            if cost > 0:
                lines.append(f"Cost:                  ${cost:.4f}")

        return "
".join(lines)

    def _format_metadata(self, metadata: Dict) -> str:
        """Format metadata."""
        lines = []

        for key, value in metadata.items():
            lines.append(f"{key:25} : {value}")

        return "
".join(lines)

    def format_compact(self, receipt: Dict) -> str:
        """
        Format a compact one-line summary.

        Useful for CLI output.
        """
        total = receipt.get("total_tokens", {})
        savings = receipt.get("savings", {})
        provider = receipt.get("provider", {})

        parts = []

        # Tokens
        charged = total.get("provider_charged", 0)
        parts.append(f"{charged:,} tokens")

        # Savings
        saved_pct = savings.get("savings_percent", 0)
        if saved_pct > 0:
            parts.append(f"({saved_pct:.0f}% saved)")

        # Cost
        cost = provider.get("cost_usd", 0)
        if cost > 0:
            parts.append(f"${cost:.4f}")

        # Provider
        provider_id = provider.get("provider_id", "")
        if provider_id:
            parts.append(f"via {provider_id}")

        return " | ".join(parts)


# Global formatter instance
_global_formatter = None


def get_formatter() -> VerboseFormatter:
    """Get the global verbose formatter."""
    global _global_formatter
    if _global_formatter is None:
        _global_formatter = VerboseFormatter()
    return _global_formatter
