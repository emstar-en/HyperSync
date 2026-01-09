"""
AGUA Runtime: Psi Module
========================

Implements ψ geodesic distance and effective ψ calculation with geometric regularization.

Functions:
- geodesic_distance(W, W_ref) -> float
  Computes Poincaré ball geodesic distance d_H(W, W_ref)

- effective(psi_codebook, W, W_ref, params) -> float
  Computes ψ_effective = ψ_codebook × (1 - λ×|d_H - μ|/σ) with EWMA smoothing
"""

import numpy as np
from typing import List, Dict, Any, Optional


def geodesic_distance(W: List[float], W_ref: List[float]) -> float:
    """
    Compute Poincaré ball geodesic distance d_H(W, W_ref).

    The Poincaré ball model uses the metric:
    d_H(x, y) = arcosh(1 + 2 * ||x - y||² / ((1 - ||x||²)(1 - ||y||²)))

    Args:
        W: Current weight vector (length 7)
        W_ref: Reference weight vector (length 7)

    Returns:
        Geodesic distance in Poincaré ball

    Raises:
        ValueError: If vectors are not length 7 or outside Poincaré ball
    """
    W = np.array(W, dtype=np.float64)
    W_ref = np.array(W_ref, dtype=np.float64)

    if len(W) != 7 or len(W_ref) != 7:
        raise ValueError(f"Weight vectors must be length 7, got {len(W)} and {len(W_ref)}")

    # Check Poincaré ball constraint: ||W|| < 1
    norm_W = np.linalg.norm(W)
    norm_W_ref = np.linalg.norm(W_ref)

    if norm_W >= 1.0:
        raise ValueError(f"W must be inside Poincaré ball: ||W|| = {norm_W:.6f} >= 1.0")
    if norm_W_ref >= 1.0:
        raise ValueError(f"W_ref must be inside Poincaré ball: ||W_ref|| = {norm_W_ref:.6f} >= 1.0")

    # Compute geodesic distance
    diff = W - W_ref
    diff_norm_sq = np.dot(diff, diff)

    # Poincaré distance formula
    numerator = 2.0 * diff_norm_sq
    denominator = (1.0 - norm_W**2) * (1.0 - norm_W_ref**2)

    # Avoid numerical issues
    if denominator < 1e-12:
        # Points are very close to boundary
        return 10.0  # Large distance

    ratio = 1.0 + numerator / denominator

    # Clamp to avoid numerical issues with arcosh
    ratio = max(1.0, ratio)

    distance = np.arccosh(ratio)

    return float(distance)


def effective(
    psi_codebook: Dict[str, Any],
    W: List[float],
    W_ref: List[float],
    params: Optional[Dict[str, Any]] = None
) -> float:
    """
    Compute effective ψ with geometric regularization.

    Formula:
    ψ_effective = ψ_codebook × (1 - λ × |d_H - μ| / σ)

    With optional EWMA smoothing:
    ψ_smooth = α × ψ_effective + (1 - α) × ψ_prev

    Args:
        psi_codebook: Codebook entry with 'psi' field
        W: Current weight vector
        W_ref: Reference weight vector
        params: Optional parameters:
            - lambda_reg: Regularization strength (default: 0.1)
            - mu: Expected distance (default: 0.5)
            - sigma: Distance scale (default: 1.0)
            - ewma_alpha: EWMA smoothing factor (default: 0.3)
            - psi_prev: Previous ψ value for EWMA (default: None)

    Returns:
        Effective ψ value with geometric regularization
    """
    if params is None:
        params = {}

    # Extract parameters with defaults
    lambda_reg = params.get('lambda_reg', 0.1)
    mu = params.get('mu', 0.5)
    sigma = params.get('sigma', 1.0)
    ewma_alpha = params.get('ewma_alpha', 0.3)
    psi_prev = params.get('psi_prev', None)

    # Get base ψ from codebook
    psi_base = psi_codebook.get('psi', 0.75)

    # Compute geodesic distance
    d_H = geodesic_distance(W, W_ref)

    # Geometric regularization term
    distance_deviation = abs(d_H - mu)
    regularization = lambda_reg * distance_deviation / sigma

    # Clamp regularization to [0, 1]
    regularization = min(1.0, max(0.0, regularization))

    # Compute effective ψ
    psi_effective = psi_base * (1.0 - regularization)

    # Apply EWMA smoothing if previous value provided
    if psi_prev is not None:
        psi_smooth = ewma_alpha * psi_effective + (1.0 - ewma_alpha) * psi_prev
        return float(psi_smooth)

    return float(psi_effective)


def lookup_psi_from_codebook(
    psi_codebook_data: Dict[str, Any],
    W: List[float],
    method: str = 'nearest'
) -> Dict[str, Any]:
    """
    Look up ψ entry from codebook based on weight vector W.

    Args:
        psi_codebook_data: Full codebook with 'codebook' list
        W: Weight vector to look up
        method: Lookup method ('nearest' or 'interpolate')

    Returns:
        Codebook entry (or interpolated entry)
    """
    codebook = psi_codebook_data.get('codebook', [])

    if not codebook:
        raise ValueError("Empty codebook")

    W = np.array(W, dtype=np.float64)

    if method == 'nearest':
        # Find nearest entry by W distance
        min_dist = float('inf')
        best_entry = codebook[0]

        for entry in codebook:
            W_entry = np.array(entry['W'], dtype=np.float64)
            dist = np.linalg.norm(W - W_entry)
            if dist < min_dist:
                min_dist = dist
                best_entry = entry

        return best_entry

    elif method == 'interpolate':
        # Linear interpolation between two nearest entries
        # For simplicity, use nearest for now
        # Full interpolation would require more sophisticated logic
        return lookup_psi_from_codebook(psi_codebook_data, W, method='nearest')

    else:
        raise ValueError(f"Unknown lookup method: {method}")


# Example usage and validation
if __name__ == "__main__":
    print("AGUA Runtime Psi Module - Validation")
    print("=" * 50)

    # Test geodesic distance
    W1 = [0.15, 0.15, 0.14, 0.14, 0.14, 0.14, 0.14]
    W2 = [0.20, 0.18, 0.15, 0.14, 0.12, 0.11, 0.10]

    d = geodesic_distance(W1, W2)
    print(f"\nGeodesic distance test:")
    print(f"  W1 = {W1}")
    print(f"  W2 = {W2}")
    print(f"  d_H(W1, W2) = {d:.6f}")

    # Test effective psi
    psi_entry = {'psi': 0.85}
    params = {
        'lambda_reg': 0.1,
        'mu': 0.5,
        'sigma': 1.0,
        'ewma_alpha': 0.3
    }

    psi_eff = effective(psi_entry, W1, W2, params)
    print(f"\nEffective ψ test:")
    print(f"  Base ψ = {psi_entry['psi']}")
    print(f"  ψ_effective = {psi_eff:.6f}")

    # Test with EWMA
    params['psi_prev'] = 0.80
    psi_smooth = effective(psi_entry, W1, W2, params)
    print(f"  ψ_smooth (with EWMA) = {psi_smooth:.6f}")

    print("\n✓ All functions operational")
