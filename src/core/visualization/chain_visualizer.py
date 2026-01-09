"""
HyperSync Delegation Chain Visualization

Generate visual representations of delegation chains (ASCII, Mermaid, DOT).
"""

from typing import Dict, List, Optional
from hypersync.agents.delegation.tracker import DelegationChain, DelegationStatus


class ChainVisualizer:
    """
    Visualize delegation chains in various formats.

    Supports ASCII art, Mermaid diagrams, and GraphViz DOT format.
    """

    @staticmethod
    def to_ascii(chain: DelegationChain, show_timing: bool = True) -> str:
        """
        Generate ASCII art representation of chain.

        Args:
            chain: Delegation chain
            show_timing: Include timing information

        Returns:
            ASCII art string
        """
        lines = []
        lines.append(f"Delegation Chain: {chain.chain_id}")
        lines.append(f"Requester: {chain.requester_id}")
        lines.append(f"Root Agent: {chain.root_agent_id}")
        lines.append(f"Depth: {chain.get_current_depth()}/{chain.max_depth}")
        lines.append("")

        if chain.has_cycle():
            cycle_agents = chain.get_cycle_agents()
            lines.append(f"⚠️  CYCLE DETECTED: {', '.join(cycle_agents)}")
            lines.append("")

        # Draw chain
        for i, node in enumerate(chain.nodes):
            indent = "  " * i
            status_icon = ChainVisualizer._get_status_icon(node.status)

            line = f"{indent}├─ {status_icon} {node.agent_id} → {node.node_id}"

            if show_timing and node.duration_ms is not None:
                line += f" ({node.duration_ms:.2f}ms)"

            if node.error:
                line += f" [ERROR: {node.error}]"

            lines.append(line)

        return "\n".join(lines)

    @staticmethod
    def to_mermaid(chain: DelegationChain) -> str:
        """
        Generate Mermaid diagram representation.

        Args:
            chain: Delegation chain

        Returns:
            Mermaid diagram string
        """
        lines = []
        lines.append("```mermaid")
        lines.append("graph TD")
        lines.append(f"    REQ[{chain.requester_id}]")

        # Add nodes
        for i, node in enumerate(chain.nodes):
            node_id = f"N{i}"
            label = f"{node.agent_id}<br/>{node.node_id}"

            if node.status == DelegationStatus.FAILED:
                lines.append(f"    {node_id}[{label}]:::failed")
            elif node.status == DelegationStatus.COMPLETED:
                lines.append(f"    {node_id}[{label}]:::completed")
            else:
                lines.append(f"    {node_id}[{label}]")

        # Add edges
        if chain.nodes:
            lines.append(f"    REQ --> N0")
            for i in range(len(chain.nodes) - 1):
                lines.append(f"    N{i} --> N{i+1}")

        # Add styles
        lines.append("    classDef failed fill:#f88,stroke:#f00")
        lines.append("    classDef completed fill:#8f8,stroke:#0f0")
        lines.append("```")

        return "\n".join(lines)

    @staticmethod
    def to_dot(chain: DelegationChain) -> str:
        """
        Generate GraphViz DOT representation.

        Args:
            chain: Delegation chain

        Returns:
            DOT format string
        """
        lines = []
        lines.append("digraph DelegationChain {")
        lines.append("    rankdir=LR;")
        lines.append("    node [shape=box];")
        lines.append("")

        # Requester node
        lines.append(f'    req [label="{chain.requester_id}\n(Requester)" shape=ellipse];')

        # Delegation nodes
        for i, node in enumerate(chain.nodes):
            node_id = f"n{i}"
            label = f"{node.agent_id}\n{node.node_id}"

            if node.duration_ms:
                label += f"\n{node.duration_ms:.2f}ms"

            color = ChainVisualizer._get_dot_color(node.status)
            lines.append(f'    {node_id} [label="{label}" color="{color}"];')

        # Edges
        if chain.nodes:
            lines.append(f"    req -> n0;")
            for i in range(len(chain.nodes) - 1):
                lines.append(f"    n{i} -> n{i+1};")

        lines.append("}")

        return "\n".join(lines)

    @staticmethod
    def to_json(chain: DelegationChain) -> Dict:
        """
        Generate JSON representation.

        Args:
            chain: Delegation chain

        Returns:
            Dictionary representation
        """
        return chain.to_dict()

    @staticmethod
    def _get_status_icon(status: DelegationStatus) -> str:
        """Get icon for status."""
        icons = {
            DelegationStatus.PENDING: "⏳",
            DelegationStatus.ACTIVE: "▶️",
            DelegationStatus.COMPLETED: "✅",
            DelegationStatus.FAILED: "❌",
            DelegationStatus.TIMEOUT: "⏱️"
        }
        return icons.get(status, "❓")

    @staticmethod
    def _get_dot_color(status: DelegationStatus) -> str:
        """Get color for DOT format."""
        colors = {
            DelegationStatus.PENDING: "gray",
            DelegationStatus.ACTIVE: "blue",
            DelegationStatus.COMPLETED: "green",
            DelegationStatus.FAILED: "red",
            DelegationStatus.TIMEOUT: "orange"
        }
        return colors.get(status, "black")


def visualize_chain(chain: DelegationChain, format: str = "ascii",
                   **kwargs) -> str:
    """
    Convenience function to visualize a chain.

    Args:
        chain: Delegation chain
        format: Output format (ascii, mermaid, dot, json)
        **kwargs: Format-specific options

    Returns:
        Visualization string
    """
    visualizer = ChainVisualizer()

    if format == "ascii":
        return visualizer.to_ascii(chain, **kwargs)
    elif format == "mermaid":
        return visualizer.to_mermaid(chain)
    elif format == "dot":
        return visualizer.to_dot(chain)
    elif format == "json":
        import json
        return json.dumps(visualizer.to_json(chain), indent=2)
    else:
        raise ValueError(f"Unknown format: {format}")
