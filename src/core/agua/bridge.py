"""
AGUA Integration Bridge
Connects AGUA mathematical implementations to main system
"""
import numpy as np
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class AGUABridge:
    """Bridge between AGUA runtime and main system."""

    def __init__(self):
        self.agua_available = self._check_agua_availability()

    def _check_agua_availability(self) -> bool:
        """Check if AGUA runtime is available."""
        try:
            # Try to import AGUA components
            import sys
            import os

            # Add AGUA runtime to path if exists
            agua_path = os.path.join(os.path.dirname(__file__), '..', 'agua_runtime')
            if os.path.exists(agua_path):
                sys.path.insert(0, agua_path)
                return True
            return False
        except Exception as e:
            logger.warning(f"AGUA runtime not available: {e}")
            return False

    def use_agua_manifold_ops(self, operation: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Use AGUA manifold operations if available.

        Args:
            operation: Operation name
            params: Operation parameters

        Returns:
            Result from AGUA or None if not available
        """
        if not self.agua_available:
            return None

        try:
            # Import AGUA manifold operations
            from manifold_operations import ManifoldOperator

            operator = ManifoldOperator()
            result = operator.execute(operation, params)

            logger.info(f"Used AGUA for {operation}")
            return result

        except Exception as e:
            logger.error(f"AGUA operation failed: {e}")
            return None

    def fallback_to_native(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback to native implementations.

        Args:
            operation: Operation name
            params: Operation parameters

        Returns:
            Result from native implementation
        """
        from runtime.geometric_implementations import run_operator
        return run_operator(operation, params)

    def execute_with_fallback(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute operation with AGUA if available, fallback to native.

        Args:
            operation: Operation name
            params: Operation parameters

        Returns:
            Operation result
        """
        # Try AGUA first
        result = self.use_agua_manifold_ops(operation, params)

        if result is not None:
            result["implementation"] = "agua"
            return result

        # Fallback to native
        result = self.fallback_to_native(operation, params)
        result["implementation"] = "native"

        return result


# Global bridge
_bridge = AGUABridge()

def get_bridge() -> AGUABridge:
    """Get global AGUA bridge."""
    return _bridge


def execute_geometric_operation(operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for geometric operations.
    Automatically uses AGUA if available, falls back to native.

    Args:
        operation: Operation name
        params: Operation parameters

    Returns:
        Operation result with implementation info
    """
    return _bridge.execute_with_fallback(operation, params)
