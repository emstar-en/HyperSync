"""
Route Loader - Auto-discovery and loading of API route modules.

Automatically discovers and loads route modules from the API routes directory.
"""
import os
import importlib
import inspect
import logging
from pathlib import Path
from typing import List, Optional, Any

from hypersync.api.router_registry import get_router_registry, RouteCategory

logger = logging.getLogger(__name__)


class RouteLoader:
    """
    Loads API routes from modules.

    Discovers route modules and registers their routes with the registry.
    """

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = base_path or self._find_routes_path()
        self.registry = get_router_registry()
        self._loaded_modules: List[str] = []

    def _find_routes_path(self) -> str:
        """Find the API routes directory path."""
        try:
            import hypersync.api.routes
            return os.path.dirname(hypersync.api.routes.__file__)
        except ImportError:
            return os.path.join(os.getcwd(), "hypersync", "api", "routes")

    def discover_routes(self) -> List[str]:
        """
        Discover all route modules in the routes directory.

        Returns:
            List of module names
        """
        if not os.path.exists(self.base_path):
            logger.warning(f"Routes path not found: {self.base_path}")
            return []

        modules = []

        for file in os.listdir(self.base_path):
            if file.endswith("_routes.py") and not file.startswith("__"):
                module_name = file[:-3]  # Remove .py
                modules.append(module_name)

        logger.info(f"Discovered {len(modules)} route modules")
        return modules

    def load_module(self, module_name: str) -> bool:
        """
        Load a route module and register its routes.

        Args:
            module_name: Name of the module (without .py)

        Returns:
            True if loaded successfully
        """
        try:
            # Import the module
            full_module_name = f"hypersync.api.routes.{module_name}"
            module = importlib.import_module(full_module_name)

            # Look for registration function
            if hasattr(module, "register_routes"):
                module.register_routes(self.registry)
                logger.info(f"Loaded routes from {module_name}")
                self._loaded_modules.append(module_name)
                return True
            else:
                logger.warning(f"Module {module_name} has no register_routes function")
                return False

        except Exception as e:
            logger.error(f"Failed to load module {module_name}: {e}", exc_info=True)
            return False

    def load_all(self) -> int:
        """
        Load all discovered route modules.

        Returns:
            Number of modules loaded successfully
        """
        modules = self.discover_routes()
        loaded_count = 0

        for module_name in modules:
            if self.load_module(module_name):
                loaded_count += 1

        logger.info(f"Loaded {loaded_count}/{len(modules)} route modules")
        return loaded_count

    def get_loaded_modules(self) -> List[str]:
        """Get list of loaded module names."""
        return self._loaded_modules.copy()


# Convenience function
def load_all_routes() -> int:
    """Load all API routes. Returns number of modules loaded."""
    loader = RouteLoader()
    return loader.load_all()
