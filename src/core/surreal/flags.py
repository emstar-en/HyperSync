"""
Surreal Feature Flags
"""
import os


def enable_mixed_cuts() -> bool:
    """Check if mixed-type operations are enabled."""
    return os.getenv("HYPERSYNC_SURREAL_MIXED_TYPES", "false").lower() == "true"


def enable_infinite_ordinals() -> bool:
    """Check if infinite ordinal support is enabled."""
    return os.getenv("HYPERSYNC_SURREAL_INFINITE", "false").lower() == "true"
