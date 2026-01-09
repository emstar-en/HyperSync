"""
CLI Command Registry - Central registry for CLI commands.

Manages registration and organization of CLI commands into groups.
"""
import logging
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class CommandCategory(Enum):
    """Categories for organizing commands."""
    CORE = "core"
    MESH = "mesh"
    SCHEDULER = "scheduler"
    GOVERNANCE = "governance"
    DEPLOYMENT = "deployment"
    TELEMETRY = "telemetry"
    SECURITY = "security"
    AGENT = "agent"
    ORCHESTRATOR = "orchestrator"
    TUI = "tui"
    DEBUG = "debug"


@dataclass
class CommandMetadata:
    """Metadata for a CLI command."""
    name: str
    handler: Callable
    category: CommandCategory
    description: str
    aliases: List[str] = field(default_factory=list)
    arguments: List[Dict[str, Any]] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    requires_auth: bool = False
    deprecated: bool = False


class CLIRegistry:
    """
    Central registry for CLI commands.

    Responsibilities:
    - Register commands with metadata
    - Organize commands into categories
    - Provide command lookup
    - Generate help text
    """

    def __init__(self):
        self._commands: Dict[str, CommandMetadata] = {}
        self._categories: Dict[CommandCategory, List[str]] = {
            cat: [] for cat in CommandCategory
        }
        self._aliases: Dict[str, str] = {}

    def register_command(
        self,
        name: str,
        handler: Callable,
        category: CommandCategory,
        description: str,
        aliases: Optional[List[str]] = None,
        arguments: Optional[List[Dict[str, Any]]] = None,
        examples: Optional[List[str]] = None,
        requires_auth: bool = False,
        deprecated: bool = False
    ) -> None:
        """
        Register a CLI command.

        Args:
            name: Command name (e.g., "mesh:list")
            handler: Function to handle the command
            category: Command category
            description: Short description
            aliases: Alternative names
            arguments: Argument specifications
            examples: Usage examples
            requires_auth: Whether command requires authentication
            deprecated: Whether command is deprecated
        """
        if name in self._commands:
            logger.warning(f"Command {name} already registered, replacing")

        metadata = CommandMetadata(
            name=name,
            handler=handler,
            category=category,
            description=description,
            aliases=aliases or [],
            arguments=arguments or [],
            examples=examples or [],
            requires_auth=requires_auth,
            deprecated=deprecated
        )

        self._commands[name] = metadata
        self._categories[category].append(name)

        # Register aliases
        for alias in metadata.aliases:
            self._aliases[alias] = name

        logger.debug(f"Registered command: {name} ({category.value})")

    def get_command(self, name: str) -> Optional[CommandMetadata]:
        """Get command metadata by name or alias."""
        # Check if it's an alias
        if name in self._aliases:
            name = self._aliases[name]

        return self._commands.get(name)

    def list_commands(
        self,
        category: Optional[CommandCategory] = None,
        include_deprecated: bool = False
    ) -> List[CommandMetadata]:
        """
        List commands, optionally filtered by category.

        Args:
            category: Filter by category (None = all)
            include_deprecated: Include deprecated commands

        Returns:
            List of command metadata
        """
        if category:
            command_names = self._categories.get(category, [])
        else:
            command_names = list(self._commands.keys())

        commands = [self._commands[name] for name in command_names]

        if not include_deprecated:
            commands = [cmd for cmd in commands if not cmd.deprecated]

        return sorted(commands, key=lambda c: c.name)

    def list_categories(self) -> List[CommandCategory]:
        """List all categories that have commands."""
        return [
            cat for cat in CommandCategory
            if len(self._categories[cat]) > 0
        ]

    def generate_help(
        self,
        command_name: Optional[str] = None
    ) -> str:
        """
        Generate help text.

        Args:
            command_name: Specific command (None = all commands)

        Returns:
            Formatted help text
        """
        if command_name:
            return self._generate_command_help(command_name)
        else:
            return self._generate_overview_help()

    def _generate_command_help(self, command_name: str) -> str:
        """Generate help for a specific command."""
        cmd = self.get_command(command_name)
        if not cmd:
            return f"Command '{command_name}' not found"

        lines = []
        lines.append(f"Command: {cmd.name}")
        lines.append(f"Category: {cmd.category.value}")
        lines.append(f"\nDescription:")
        lines.append(f"  {cmd.description}")

        if cmd.aliases:
            lines.append(f"\nAliases: {', '.join(cmd.aliases)}")

        if cmd.arguments:
            lines.append(f"\nArguments:")
            for arg in cmd.arguments:
                arg_name = arg.get("name", "")
                arg_desc = arg.get("description", "")
                arg_required = " (required)" if arg.get("required") else ""
                lines.append(f"  {arg_name}{arg_required}")
                lines.append(f"    {arg_desc}")

        if cmd.examples:
            lines.append(f"\nExamples:")
            for example in cmd.examples:
                lines.append(f"  {example}")

        if cmd.deprecated:
            lines.append(f"\n⚠️  This command is deprecated")

        if cmd.requires_auth:
            lines.append(f"\n🔒 This command requires authentication")

        return "\n".join(lines)

    def _generate_overview_help(self) -> str:
        """Generate overview help for all commands."""
        lines = []
        lines.append("HyperSync CLI")
        lines.append("=" * 50)
        lines.append("")

        for category in self.list_categories():
            commands = self.list_commands(category=category)
            if not commands:
                continue

            lines.append(f"\n{category.value.upper()} Commands:")
            lines.append("-" * 50)

            for cmd in commands:
                deprecated_mark = " [DEPRECATED]" if cmd.deprecated else ""
                lines.append(f"  {cmd.name:<30} {cmd.description}{deprecated_mark}")

        lines.append("")
        lines.append("Use 'hypersync help <command>' for detailed help")

        return "\n".join(lines)

    def get_status(self) -> Dict[str, Any]:
        """Get registry status."""
        return {
            "total_commands": len(self._commands),
            "total_aliases": len(self._aliases),
            "categories": {
                cat.value: len(self._categories[cat])
                for cat in CommandCategory
            },
            "deprecated_commands": len([
                cmd for cmd in self._commands.values()
                if cmd.deprecated
            ])
        }


# Global registry instance
_registry: Optional[CLIRegistry] = None


def get_cli_registry() -> CLIRegistry:
    """Get the global CLI registry instance."""
    global _registry
    if _registry is None:
        _registry = CLIRegistry()
    return _registry
