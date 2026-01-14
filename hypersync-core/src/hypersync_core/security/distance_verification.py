"""Distance Verification

Verify geometric distances for integrity checking.
Detect tampering via distance signature verification.

Complexity: O(n)
Security: Geometric integrity verification
"""

import numpy as np
import hashlib
from typing import Tuple
from ..geometry.hyperbolic import hyperbolic_distance


def compute_distance_signature(
    point_a: np.ndarray,
    point_b: np.ndarray,
    secret: bytes = None
) -> Tuple[float, bytes]:
    """Compute signed distance for integrity verification.
    
    Args:
        point_a: First point
        point_b: Second point
        secret: Optional secret for HMAC
    
    Returns:
        distance: Computed distance
        signature: Distance signature (hash)
    
    Complexity: O(n)
    """
    distance = hyperbolic_distance(point_a, point_b)
    
    # Create signature
    data = f"{distance:.12f}".encode()
    if secret:
        data = data + secret
    
    signature = hashlib.sha256(data).digest()
    
    return distance, signature


def verify_distance(
    point_a: np.ndarray,
    point_b: np.ndarray,
    claimed_distance: float,
    signature: bytes,
    secret: bytes = None,
    tolerance: float = 1e-9
) -> bool:
    """Verify distance signature for integrity.
    
    Args:
        point_a: First point
        point_b: Second point
        claimed_distance: Claimed distance value
        signature: Distance signature to verify
        secret: Optional secret for HMAC
        tolerance: Numerical tolerance
    
    Returns:
        valid: True if signature is valid
    
    Complexity: O(n)
    """
    # Recompute distance and signature
    actual_distance, expected_signature = compute_distance_signature(
        point_a, point_b, secret
    )
    
    # Verify distance matches
    distance_match = abs(actual_distance - claimed_distance) < tolerance
    
    # Verify signature matches
    signature_match = signature == expected_signature
    
    return distance_match and signature_match
