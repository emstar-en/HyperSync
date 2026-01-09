"""
Command Loader - Auto-discovery and loading of CLI command modules.

Automatically discovers and loads command modules from the CLI directory.
"""
import os
import sys
import importlib
import inspect
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from hypersync.cli.registry import get_cli_registry, CommandCategory

logger = logging.getLogger(__name__)


class CommandLoader:
    """
    Loads CLI commands from modules.

    Discovers command modules and registers their commands with the registry.
    """

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = base_path or self._find_cli_path()
        self.registry = get_cli_registry()
        self._loaded_modules: List[str] = []

    def _find_cli_path(self) -> str:
        """Find the CLI directory path."""
        # Try to find hypersync/cli directory
        try:
            import hypersync.cli
            return os.path.dirname(hypersync.cli.__file__)
        except ImportError:
            # Fallback to relative path
            return os.path.join(os.getcwd(), "hypersync", "cli")

    def discover_commands(self) -> List[str]:
        """
        Discover all command modules in the CLI directory.

        Returns:
            List of module names
        """
        if not os.path.exists(self.base_path):
            logger.warning(f"CLI path not found: {self.base_path}")
            return []

        modules = []

        for file in os.listdir(self.base_path):
            if file.endswith("_commands.py"):
                module_name = file[:-3]  # Remove .py
                modules.append(module_name)

        logger.info(f"Discovered {len(modules)} command modules")
        return modules

    def load_module(self, module_name: str) -> bool:
        """
        Load a command module and register its commands.

        Args:
            module_name: Name of the module (without .py)

        Returns:
            True if loaded successfully
        """
        try:
            # Import the module
            full_module_name = f"hypersync.cli.{module_name}"
            module = importlib.import_module(full_module_name)

            # Look for registration function
            if hasattr(module, "register_commands"):
                module.register_commands(self.registry)
                logger.info(f"Loaded commands from {module_name}")
                self._loaded_modules.append(module_name)
                return True
            else:
                # Try to auto-register functions
                self._auto_register_module(module, module_name)
                self._loaded_modules.append(module_name)
                return True

        except Exception as e:
            logger.error(f"Failed to load module {module_name}: {e}", exc_info=True)
            return False

    def _auto_register_module(self, module: Any, module_name: str) -> None:
        """
        Auto-register commands from a module.

        Looks for functions with specific naming patterns or decorators.
        """
        # Infer category from module name
        category = self._infer_category(module_name)

        # Find command functions
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj):
                # Check if it looks like a command
                if name.startswith("cmd_") or name.endswith("_command"):
                    command_name = self._format_command_name(name, category)
                    description = self._extract_description(obj)

                    self.registry.register_command(
                        name=command_name,
                        handler=obj,
                        category=category,
                        description=description
                    )
                    logger.debug(f"Auto-registered: {command_name}")

    def _infer_category(self, module_name: str) -> CommandCategory:
        """Infer command category from module name."""
        name_lower = module_name.lower()

        if "mesh" in name_lower:
            return CommandCategory.MESH
        elif "scheduler" in name_lower or "schedule" in name_lower:
            return CommandCategory.SCHEDULER
        elif "governance" in name_lower or "policy" in name_lower:
            return CommandCategory.GOVERNANCE
        elif "deployment" in name_lower or "deploy" in name_lower:
            return CommandCategory.DEPLOYMENT
        elif "telemetry" in name_lower or "metrics" in name_lower:
            return CommandCategory.TELEMETRY
        elif "security" in name_lower or "auth" in name_lower:
            return CommandCategory.SECURITY
        elif "agent" in name_lower:
            return CommandCategory.AGENT
        elif "orchestrator" in name_lower or "orchestration" in name_lower:
            return CommandCategory.ORCHESTRATOR
        elif "tui" in name_lower or "ui" in name_lower:
            return CommandCategory.TUI
        elif "debug" in name_lower or "test" in name_lower:
            return CommandCategory.DEBUG
        else:
            return CommandCategory.CORE

    def _format_command_name(self, func_name: str, category: CommandCategory) -> str:
        """Format function name into command name."""
        # Remove prefixes/suffixes
        name = func_name.replace("cmd_", "").replace("_command", "")

        # Convert to kebab-case
        name = name.replace("_", "-")

        # Add category prefix
        return f"{category.value}:{name}"

    def _extract_description(self, func: Any) -> str:
        """Extract description from function docstring."""
        doc = inspect.getdoc(func)
        if doc:
            # Get first line of docstring
            return doc.split("\n")[0].strip()
        return "No description available"

    def load_all(self) -> int:
        """
        Load all discovered command modules.

        Returns:
            Number of modules loaded successfully
        """
        modules = self.discover_commands()
        loaded_count = 0

        for module_name in modules:
            if self.load_module(module_name):
                loaded_count += 1

        logger.info(f"Loaded {loaded_count}/{len(modules)} command modules")
        return loaded_count

    def get_loaded_modules(self) -> List[str]:
        """Get list of loaded module names."""
        return self._loaded_modules.copy()


# Convenience function
def load_all_commands() -> int:
    """Load all CLI commands. Returns number of modules loaded."""
    loader = CommandLoader()
    return loader.load_all()
