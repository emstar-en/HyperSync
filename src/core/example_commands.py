"""
Example Command Module - Template for creating command modules.

This shows how to structure a command module for auto-discovery.
"""
import logging
from argparse import Namespace

from hypersync.cli.registry import CLIRegistry, CommandCategory

logger = logging.getLogger(__name__)


def register_commands(registry: CLIRegistry):
    """
    Register commands with the CLI registry.

    This function is called by the command loader.

    Args:
        registry: The CLI registry instance
    """

    # Register mesh:list command
    registry.register_command(
        name="mesh:list",
        handler=cmd_mesh_list,
        category=CommandCategory.MESH,
        description="List all mesh nodes",
        aliases=["mesh:ls"],
        arguments=[
            {
                "name": "--format",
                "type": str,
                "default": "table",
                "description": "Output format (table, json, yaml)"
            },
            {
                "name": "--filter",
                "type": str,
                "description": "Filter nodes by status"
            }
        ],
        examples=[
            "hypersync mesh:list",
            "hypersync mesh:list --format json",
            "hypersync mesh:list --filter active"
        ]
    )

    # Register mesh:status command
    registry.register_command(
        name="mesh:status",
        handler=cmd_mesh_status,
        category=CommandCategory.MESH,
        description="Show mesh network status",
        arguments=[
            {
                "name": "node_id",
                "type": str,
                "required": False,
                "description": "Specific node ID (optional)"
            }
        ],
        examples=[
            "hypersync mesh:status",
            "hypersync mesh:status node-123"
        ]
    )


def cmd_mesh_list(args: Namespace) -> int:
    """
    List all mesh nodes.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 = success)
    """
    logger.info("Listing mesh nodes...")

    output_format = getattr(args, "format", "table")
    filter_status = getattr(args, "filter", None)

    # TODO: Implement actual mesh listing logic
    print(f"Mesh nodes (format: {output_format}):")
    print("  node-1: active")
    print("  node-2: active")
    print("  node-3: inactive")

    return 0


def cmd_mesh_status(args: Namespace) -> int:
    """
    Show mesh network status.

    Args:
        args: Parsed command line arguments

    Returns:
        Exit code (0 = success)
    """
    node_id = getattr(args, "node_id", None)

    if node_id:
        logger.info(f"Getting status for node: {node_id}")
        print(f"Node {node_id} status: active")
    else:
        logger.info("Getting mesh network status...")
        print("Mesh Network Status:")
        print("  Total nodes: 3")
        print("  Active nodes: 2")
        print("  Inactive nodes: 1")
        print("  Network health: 85%")

    return 0
