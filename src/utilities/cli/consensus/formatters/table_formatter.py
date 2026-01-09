"""
Table formatter for CLI output
"""

from typing import List, Dict

class TableFormatter:
    """Formats data as ASCII tables."""

    @staticmethod
    def format_mechanisms(mechanisms: List[Dict]) -> str:
        """Format mechanisms list as table."""
        if not mechanisms:
            return "No mechanisms found"

        lines = []
        lines.append(f"{'ID':<25} {'Name':<30} {'Weight':<15} {'Use'}")
        lines.append("-" * 100)

        for mech in mechanisms:
            lines.append(
                f"{mech['id']:<25} {mech['name']:<30} "
                f"{mech['weight']:<15} {mech.get('primary_use', 'N/A')}"
            )

        return "\n".join(lines)

    @staticmethod
    def format_tier_capabilities(capabilities: Dict) -> str:
        """Format tier capabilities as table."""
        lines = []
        lines.append(f"\nTier: {capabilities['tier_id']}")
        lines.append(f"Mechanisms: {capabilities['mechanisms_count']}")
        lines.append("\nResource Limits:")

        limits = capabilities['resource_limits']
        lines.append(f"  Max Nodes: {limits['max_nodes'] or 'Unlimited'}")
        lines.append(f"  Max Dimensions: {limits['max_dimensions']}")
        lines.append(f"  Max Memory: {limits['max_memory_mb']}MB")

        lines.append("\nFeatures:")
        for feature, enabled in capabilities['features'].items():
            status = "✓" if enabled else "✗"
            lines.append(f"  {status} {feature}")

        return "\n".join(lines)
