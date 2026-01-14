"""Security Module

Provides 6 Core tier security operations:
1. Hyperbolic Encryption - Geometric encryption using hyperbolic distance
2. Curvature Authentication - Auth using curvature signatures
3. Geodesic Authorization - Access control via geodesic proximity
4. Distance Verification - Verify distances for integrity
5. Proximity Adversarial Detection - Detect adversarial nodes
6. OpenSSL Integration - Standard cryptographic operations

All operations leverage geometric properties for security.
"""

from .hyperbolic_encryption import hyperbolic_encrypt, hyperbolic_decrypt
from .curvature_auth import curvature_authenticate, generate_curvature_token
from .geodesic_authorization import geodesic_authorize, check_proximity
from .distance_verification import verify_distance, compute_distance_signature
from .proximity_adversarial import detect_adversarial_nodes, compute_proximity_score
from .openssl_integration import generate_key_pair, sign_message, verify_signature

__all__ = [
    "hyperbolic_encrypt",
    "hyperbolic_decrypt",
    "curvature_authenticate",
    "generate_curvature_token",
    "geodesic_authorize",
    "check_proximity",
    "verify_distance",
    "compute_distance_signature",
    "detect_adversarial_nodes",
    "compute_proximity_score",
    "generate_key_pair",
    "sign_message",
    "verify_signature",
]
