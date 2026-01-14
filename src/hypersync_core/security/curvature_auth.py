"""Curvature-Based Authentication

Authentication using geometric curvature signatures.
Each identity has a unique curvature profile.

Complexity: O(n)
Security: Curvature-based identity binding
"""

import numpy as np
import hashlib
from typing import Dict, Tuple


def generate_curvature_token(identity: str, secret: bytes) -> Dict:
    """Generate authentication token based on curvature signature.
    
    Args:
        identity: User/node identity
        secret: Secret key
    
    Returns:
        token: Authentication token with curvature signature
    
    Complexity: O(n)
    """
    # Generate identity-specific curvature
    combined = identity.encode() + secret
    hash_value = hashlib.sha256(combined).digest()
    
    # Convert to curvature vector
    seed = int.from_bytes(hash_value[:8], 'big')
    np.random.seed(seed)
    
    curvature_signature = np.random.randn(16)  # 16D curvature signature
    curvature_signature = curvature_signature / np.linalg.norm(curvature_signature)
    
    token = {
        'identity': identity,
        'curvature_signature': curvature_signature.tolist(),
        'hash': hash_value.hex(),
    }
    
    return token


def curvature_authenticate(token: Dict, secret: bytes) -> bool:
    """Authenticate using curvature signature verification.
    
    Args:
        token: Authentication token
        secret: Secret key
    
    Returns:
        valid: True if authentication succeeds
    
    Complexity: O(n)
    """
    identity = token['identity']
    claimed_signature = np.array(token['curvature_signature'])
    
    # Regenerate expected signature
    expected_token = generate_curvature_token(identity, secret)
    expected_signature = np.array(expected_token['curvature_signature'])
    
    # Verify signature matches
    distance = np.linalg.norm(claimed_signature - expected_signature)
    
    return distance < 1e-6
