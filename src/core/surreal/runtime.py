"""
Surreal Number Runtime with Fallbacks
Provides safe mixed-type operations with feature flags.
"""
from typing import Any, Union
from surreal.flags import enable_mixed_cuts
import logging

logger = logging.getLogger(__name__)


class SurrealUnsupportedError(Exception):
    """Raised when surreal operation is not supported."""
    pass


def safe_add(a: Any, b: Any) -> Any:
    """
    Safely add two surreal numbers with fallback.

    Args:
        a, b: Surreal numbers (may be mixed types)

    Returns:
        Sum or raises SurrealUnsupportedError
    """
    if enable_mixed_cuts():
        # Convert to common representation
        from surreal.conversion import conway_cut_to_dyadic
        a_dyadic = conway_cut_to_dyadic(a)
        b_dyadic = conway_cut_to_dyadic(b)
        return a_dyadic.add(b_dyadic)

    # Check if same type
    if type(a) != type(b):
        logger.warning(f"Mixed-type addition not enabled: {type(a)} + {type(b)}")
        raise SurrealUnsupportedError(
            "Mixed addition requires mixed_type_support flag"
        )

    # Same type - use native addition
    return a + b


def safe_multiply(a: Any, b: Any) -> Any:
    """
    Safely multiply two surreal numbers with fallback.
    """
    if enable_mixed_cuts():
        from surreal.conversion import conway_cut_to_dyadic
        a_dyadic = conway_cut_to_dyadic(a)
        b_dyadic = conway_cut_to_dyadic(b)
        return a_dyadic.multiply(b_dyadic)

    if type(a) != type(b):
        logger.warning(f"Mixed-type multiplication not enabled")
        raise SurrealUnsupportedError(
            "Mixed multiplication requires mixed_type_support flag"
        )

    return a * b


def safe_compare(a: Any, b: Any) -> int:
    """
    Safely compare two surreal numbers.

    Returns:
        -1 if a < b, 0 if a == b, 1 if a > b
    """
    if enable_mixed_cuts():
        from surreal.conversion import conway_cut_to_dyadic
        a_dyadic = conway_cut_to_dyadic(a)
        b_dyadic = conway_cut_to_dyadic(b)
        return a_dyadic.compare(b_dyadic)

    if type(a) != type(b):
        raise SurrealUnsupportedError(
            "Mixed comparison requires mixed_type_support flag"
        )

    if a < b:
        return -1
    elif a > b:
        return 1
    else:
        return 0
