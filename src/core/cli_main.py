"""
Main CLI Entry Point - Unified CLI with all command namespaces.

This is the main entry point that wires all command modules together.
"""
import sys
import argparse
import logging
from typing import List, Optional

from hypersync.cli.registry import get_cli_registry, CommandCategory
from hypersync.cli.command_loader import load_all_commands
from hypersync.cli.command_groups import list_groups

logger = logging.getLogger(__name__)


class HyperSyncCLI:
    """Main CLI application."""

    def __init__(self):
        self.registry = get_cli_registry()
        self.parser = None
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def initialize(self):
        """Initialize the CLI by loading all commands."""
        logger.info("Initializing HyperSync CLI...")

        # Load all command modules
        loaded_count = load_all_commands()
        logger.info(f"Loaded {loaded_count} command modules")

        # Build argument parser
        self._build_parser()

        logger.info("CLI initialization complete")

    def _build_parser(self):
        """Build the argument parser with all commands."""
        self.parser = argparse.ArgumentParser(
            prog="hypersync",
            description="HyperSync - Hyperbolic Orchestration Platform",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        # Global options
        self.parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug logging"
        )

        self.parser.add_argument(
            "--config",
            type=str,
            help="Path to configuration file"
        )

        self.parser.add_argument(
            "--version",
            action="version",
            version="HyperSync 1.0.0"
        )

        # Subparsers for commands
        subparsers = self.parser.add_subparsers(
            dest="command",
            help="Available commands"
        )

        # Add help command
        help_parser = subparsers.add_parser(
            "help",
            help="Show help for commands"
        )
        help_parser.add_argument(
            "topic",
            nargs="?",
            help="Command or topic to get help for"
        )

        # Add commands by category
        for category in CommandCategory:
            commands = self.registry.list_commands(category=category)

            for cmd in commands:
                # Parse command name (e.g., "mesh:list" -> "mesh", "list")
                if ":" in cmd.name:
                    group, subcommand = cmd.name.split(":", 1)
                else:
                    group = "core"
                    subcommand = cmd.name

                # Create parser for this command
                cmd_parser = subparsers.add_parser(
                    cmd.name,
                    help=cmd.description,
                    aliases=cmd.aliases
                )

                # Add arguments
                for arg in cmd.arguments:
                    arg_name = arg.get("name", "")
                    arg_type = arg.get("type", str)
                    arg_required = arg.get("required", False)
                    arg_help = arg.get("description", "")
                    arg_default = arg.get("default")

                    if arg_required:
                        cmd_parser.add_argument(
                            arg_name,
                            type=arg_type,
                            help=arg_help
                        )
                    else:
                        cmd_parser.add_argument(
                            arg_name,
                            type=arg_type,
                            default=arg_default,
                            nargs="?",
                            help=arg_help
                        )

    def run(self, args: Optional[List[str]] = None):
        """
        Run the CLI.

        Args:
            args: Command line arguments (None = sys.argv)
        """
        if args is None:
            args = sys.argv[1:]

        # Parse arguments
        parsed_args = self.parser.parse_args(args)

        # Handle debug flag
        if parsed_args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Debug logging enabled")

        # Handle help command
        if parsed_args.command == "help":
            self._handle_help(parsed_args.topic if hasattr(parsed_args, "topic") else None)
            return 0

        # Handle no command
        if not parsed_args.command:
            self.parser.print_help()
            return 0

        # Execute command
        return self._execute_command(parsed_args)

    def _handle_help(self, topic: Optional[str]):
        """Handle help command."""
        if topic:
            # Show help for specific command
            help_text = self.registry.generate_help(topic)
            print(help_text)
        else:
            # Show overview
            help_text = self.registry.generate_help()
            print(help_text)

    def _execute_command(self, args):
        """Execute a command."""
        command_name = args.command

        # Get command metadata
        cmd = self.registry.get_command(command_name)

        if not cmd:
            logger.error(f"Command not found: {command_name}")
            return 1

        # Check if deprecated
        if cmd.deprecated:
            logger.warning(f"Command '{command_name}' is deprecated")

        try:
            # Call command handler
            logger.debug(f"Executing command: {command_name}")
            result = cmd.handler(args)

            # Handle return value
            if result is None:
                return 0
            elif isinstance(result, int):
                return result
            else:
                return 0

        except Exception as e:
            logger.error(f"Command execution failed: {e}", exc_info=True)
            return 1


def main():
    """Main entry point for the CLI."""
    cli = HyperSyncCLI()
    cli.initialize()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
