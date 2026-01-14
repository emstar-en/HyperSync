"""Geodesic-Based Authorization

Access control using geodesic proximity.
Authorization granted if geodesic distance is below threshold.

Complexity: O(n)
Security: Geometric proximity-based access control
"""

import numpy as np
from typing import Dict
from ..geometry.hyperbolic import hyperbolic_distance


def geodesic_authorize(
    requester_position: np.ndarray,
    resource_position: np.ndarray,
    max_distance: float = 1.0
) -> bool:
    """Authorize access based on geodesic proximity.
    
    Args:
        requester_position: Position of requesting entity in Poincaré ball
        resource_position: Position of resource in Poincaré ball
        max_distance: Maximum allowed geodesic distance
    
    Returns:
        authorized: True if access granted
    
    Complexity: O(n)
    """
    distance = hyperbolic_distance(requester_position, resource_position)
    
    return distance <= max_distance


def check_proximity(
    positions: Dict[str, np.ndarray],
    resource: str,
    requester: str,
    max_distance: float = 1.0
) -> bool:
    """Check if requester is within authorized proximity of resource.
    
    Args:
        positions: Dictionary mapping entity IDs to positions
        resource: Resource ID
        requester: Requester ID
        max_distance: Maximum allowed distance
    
    Returns:
        authorized: True if within proximity
    
    Complexity: O(n)
    """
    if resource not in positions or requester not in positions:
        return False
    
    return geodesic_authorize(
        positions[requester],
        positions[resource],
        max_distance
    )
