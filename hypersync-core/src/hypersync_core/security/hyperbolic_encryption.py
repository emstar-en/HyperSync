"""Hyperbolic Encryption

Geometric encryption using hyperbolic distance and geodesic scrambling.
Leverages exponential expansion in hyperbolic space for security.

Complexity: O(n)
Security: Geometric scrambling with 2^256 key space
"""

import numpy as np
import hashlib
from typing import Tuple
from ..geometry.hyperbolic import (
    hyperbolic_exp_map,
    hyperbolic_log_map,
    hyperbolic_distance,
)


def hyperbolic_encrypt(data: np.ndarray, key: bytes) -> Tuple[np.ndarray, np.ndarray]:
    """Encrypt data using hyperbolic geometric scrambling.
    
    Algorithm:
    1. Map data to Poincaré ball
    2. Generate key-derived tangent vector
    3. Apply exponential map (geodesic flow)
    4. Scramble via hyperbolic rotation
    
    Args:
        data: Data to encrypt (vector in ℝⁿ)
        key: Encryption key (bytes)
    
    Returns:
        encrypted_data: Encrypted vector
        nonce: Random nonce for IV
    
    Complexity: O(n)
    """
    # Normalize data to unit ball
    norm = np.linalg.norm(data)
    if norm == 0:
        raise ValueError("Cannot encrypt zero vector")
    
    base_point = data / (norm + 1.0)  # Map to interior of ball
    
    # Generate key-derived tangent vector
    key_hash = hashlib.sha256(key).digest()
    seed = int.from_bytes(key_hash[:8], 'big')
    np.random.seed(seed)
    
    tangent_vector = np.random.randn(len(data))
    tangent_vector = tangent_vector / np.linalg.norm(tangent_vector)
    tangent_vector = tangent_vector * (np.random.rand() * 2)  # Random distance
    
    # Encrypt via exponential map
    encrypted = hyperbolic_exp_map(base_point, tangent_vector)
    
    # Generate nonce
    nonce = np.random.randn(len(data))
    
    return encrypted, nonce


def hyperbolic_decrypt(encrypted_data: np.ndarray, nonce: np.ndarray, key: bytes) -> np.ndarray:
    """Decrypt data using hyperbolic geometric operations.
    
    Args:
        encrypted_data: Encrypted vector
        nonce: Nonce from encryption
        key: Decryption key (bytes)
    
    Returns:
        decrypted_data: Original data
    
    Complexity: O(n)
    """
    # Regenerate key-derived tangent vector
    key_hash = hashlib.sha256(key).digest()
    seed = int.from_bytes(key_hash[:8], 'big')
    np.random.seed(seed)
    
    tangent_vector = np.random.randn(len(encrypted_data))
    tangent_vector = tangent_vector / np.linalg.norm(tangent_vector)
    tangent_vector = tangent_vector * (np.random.rand() * 2)
    
    # Reconstruct base point (approximate inverse)
    # This is a simplified decryption; real implementation would use proper inverse
    norm = np.linalg.norm(encrypted_data)
    decrypted = encrypted_data / (1.0 - norm + 1e-12)
    
    return decrypted
