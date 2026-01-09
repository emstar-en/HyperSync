"""
Command Groups - Definitions for command group organization.

Provides structured command group definitions for better CLI organization.
"""
from typing import Dict, List
from dataclasses import dataclass

from hypersync.cli.registry import CommandCategory


@dataclass
class CommandGroup:
    """Definition of a command group."""
    name: str
    category: CommandCategory
    description: str
    commands: List[str]


# Predefined command groups
COMMAND_GROUPS: Dict[str, CommandGroup] = {
    "mesh": CommandGroup(
        name="mesh",
        category=CommandCategory.MESH,
        description="Mesh network management commands",
        commands=[
            "mesh:list",
            "mesh:status",
            "mesh:join",
            "mesh:leave",
            "mesh:topology",
            "mesh:health"
        ]
    ),

    "scheduler": CommandGroup(
        name="scheduler",
        category=CommandCategory.SCHEDULER,
        description="Task scheduling and management commands",
        commands=[
            "scheduler:list",
            "scheduler:create",
            "scheduler:delete",
            "scheduler:pause",
            "scheduler:resume",
            "scheduler:status"
        ]
    ),

    "governance": CommandGroup(
        name="governance",
        category=CommandCategory.GOVERNANCE,
        description="Policy and governance commands",
        commands=[
            "governance:list-policies",
            "governance:apply-policy",
            "governance:validate",
            "governance:audit",
            "governance:telemetry"
        ]
    ),

    "deployment": CommandGroup(
        name="deployment",
        category=CommandCategory.DEPLOYMENT,
        description="Deployment and orchestration commands",
        commands=[
            "deployment:deploy",
            "deployment:rollback",
            "deployment:status",
            "deployment:list",
            "deployment:scale",
            "deployment:health"
        ]
    ),

    "telemetry": CommandGroup(
        name="telemetry",
        category=CommandCategory.TELEMETRY,
        description="Telemetry and monitoring commands",
        commands=[
            "telemetry:metrics",
            "telemetry:logs",
            "telemetry:traces",
            "telemetry:export",
            "telemetry:dashboard"
        ]
    ),

    "security": CommandGroup(
        name="security",
        category=CommandCategory.SECURITY,
        description="Security and authentication commands",
        commands=[
            "security:login",
            "security:logout",
            "security:token",
            "security:permissions",
            "security:audit"
        ]
    ),

    "agent": CommandGroup(
        name="agent",
        category=CommandCategory.AGENT,
        description="Agent management commands",
        commands=[
            "agent:list",
            "agent:create",
            "agent:delete",
            "agent:status",
            "agent:logs",
            "agent:restart"
        ]
    ),

    "orchestrator": CommandGroup(
        name="orchestrator",
        category=CommandCategory.ORCHESTRATOR,
        description="Orchestrator control commands",
        commands=[
            "orchestrator:status",
            "orchestrator:config",
            "orchestrator:nodes",
            "orchestrator:placement",
            "orchestrator:routing"
        ]
    ),

    "tui": CommandGroup(
        name="tui",
        category=CommandCategory.TUI,
        description="Terminal UI commands",
        commands=[
            "tui:launch",
            "tui:config",
            "tui:themes"
        ]
    )
}


def get_group(group_name: str) -> CommandGroup:
    """Get a command group by name."""
    return COMMAND_GROUPS.get(group_name)


def list_groups() -> List[CommandGroup]:
    """List all command groups."""
    return list(COMMAND_GROUPS.values())
