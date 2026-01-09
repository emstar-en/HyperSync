"""
AGUA Runtime: Mapping Module
=============================

Maps vendor parameters κ to weight vector W using linear and kernel transforms.

Functions:
- linear_kappa_to_W(kappa, A, intercept=None) -> list
  Linear map: W = A·κ + b, returns length-7 list

- kernel_kappa_to_W(kappa, params) -> list
  RBF kernel regression with calibration data, envelope-aware

- _rbf_kernel_matrix(X, gamma) -> ndarray
  Helper: computes RBF kernel matrix K_ij = exp(-γ||x_i - x_j||²)
"""

import numpy as np
from typing import List, Dict, Any, Optional


def linear_kappa_to_W(
    kappa: Dict[str, float],
    A: np.ndarray,
    intercept: Optional[np.ndarray] = None
) -> List[float]:
    """
    Linear mapping from vendor parameters κ to weight vector W.

    Formula: W = A·κ + b

    Args:
        kappa: Dictionary of vendor parameters
        A: Transformation matrix (7 x n_params)
        intercept: Bias vector (length 7), optional

    Returns:
        Weight vector W as list of length 7

    Raises:
        ValueError: If dimensions don't match or W is outside Poincaré ball
    """
    # Convert kappa dict to vector (sorted by key for consistency)
    kappa_keys = sorted(kappa.keys())
    kappa_vec = np.array([kappa[k] for k in kappa_keys], dtype=np.float64)

    # Check dimensions
    if A.shape[1] != len(kappa_vec):
        raise ValueError(f"A has {A.shape[1]} columns but kappa has {len(kappa_vec)} parameters")

    if A.shape[0] != 7:
        raise ValueError(f"A must have 7 rows for W vector, got {A.shape[0]}")

    # Compute W = A·κ + b
    W = A @ kappa_vec

    if intercept is not None:
        intercept = np.array(intercept, dtype=np.float64)
        if len(intercept) != 7:
            raise ValueError(f"Intercept must be length 7, got {len(intercept)}")
        W = W + intercept

    # Check Poincaré ball constraint
    W_norm = np.linalg.norm(W)
    if W_norm >= 1.0:
        # Project onto ball with margin
        margin = 0.01
        W = W * (1.0 - margin) / W_norm

    return W.tolist()


def _rbf_kernel_matrix(X: np.ndarray, gamma: float) -> np.ndarray:
    """
    Compute RBF (Gaussian) kernel matrix.

    K_ij = exp(-γ ||x_i - x_j||²)

    Args:
        X: Data matrix (n_samples x n_features)
        gamma: RBF kernel parameter

    Returns:
        Kernel matrix K (n_samples x n_samples)
    """
    # Compute pairwise squared distances
    # ||x_i - x_j||² = ||x_i||² + ||x_j||² - 2⟨x_i, x_j⟩
    X_norm_sq = np.sum(X**2, axis=1, keepdims=True)
    distances_sq = X_norm_sq + X_norm_sq.T - 2 * (X @ X.T)

    # Compute kernel matrix
    K = np.exp(-gamma * distances_sq)

    return K


def kernel_kappa_to_W(
    kappa: Dict[str, float],
    params: Dict[str, Any]
) -> List[float]:
    """
    Kernel-based mapping from κ to W using RBF kernel regression.

    Uses calibration data (κ_train, W_train) to learn non-linear mapping.

    Formula:
    W(κ) = Σᵢ αᵢ K(κ, κᵢ) Wᵢ

    Where K is RBF kernel and αᵢ are learned weights.

    Args:
        kappa: Dictionary of vendor parameters
        params: Parameters including:
            - kappa_train: List of training κ dictionaries
            - W_train: List of training W vectors
            - gamma: RBF kernel parameter (default: 1.0)
            - regularization: Ridge regularization (default: 1e-6)
            - envelope_aware: Apply envelope constraints (default: True)

    Returns:
        Weight vector W as list of length 7
    """
    # Extract parameters
    kappa_train = params.get('kappa_train', [])
    W_train = params.get('W_train', [])
    gamma = params.get('gamma', 1.0)
    regularization = params.get('regularization', 1e-6)
    envelope_aware = params.get('envelope_aware', True)

    if not kappa_train or not W_train:
        raise ValueError("kernel_kappa_to_W requires training data (kappa_train, W_train)")

    if len(kappa_train) != len(W_train):
        raise ValueError(f"Training data size mismatch: {len(kappa_train)} vs {len(W_train)}")

    # Convert training data to matrices
    kappa_keys = sorted(kappa.keys())

    # Training κ matrix
    X_train = np.array([
        [k_dict.get(key, 0.0) for key in kappa_keys]
        for k_dict in kappa_train
    ], dtype=np.float64)

    # Training W matrix
    Y_train = np.array(W_train, dtype=np.float64)

    if Y_train.shape[1] != 7:
        raise ValueError(f"W_train must have 7 columns, got {Y_train.shape[1]}")

    # Query point
    x_query = np.array([kappa[k] for k in kappa_keys], dtype=np.float64).reshape(1, -1)

    # Compute kernel matrix K_train (n_train x n_train)
    K_train = _rbf_kernel_matrix(X_train, gamma)

    # Add regularization to diagonal
    K_train_reg = K_train + regularization * np.eye(len(K_train))

    # Compute kernel vector k_query (n_train,)
    # k_query[i] = K(x_query, x_train[i])
    distances_sq = np.sum((X_train - x_query)**2, axis=1)
    k_query = np.exp(-gamma * distances_sq)

    # Solve for weights: α = K_train_reg^{-1} Y_train
    # Then W = k_query^T α = k_query^T K_train_reg^{-1} Y_train
    try:
        alpha = np.linalg.solve(K_train_reg, Y_train)
        W = k_query @ alpha
    except np.linalg.LinAlgError:
        # Fallback to pseudo-inverse
        alpha = np.linalg.lstsq(K_train_reg, Y_train, rcond=None)[0]
        W = k_query @ alpha

    # Apply envelope constraints if requested
    if envelope_aware:
        # Ensure W is inside Poincaré ball
        W_norm = np.linalg.norm(W)
        if W_norm >= 1.0:
            margin = 0.01
            W = W * (1.0 - margin) / W_norm

        # Ensure W components are non-negative (optional constraint)
        W = np.maximum(W, 0.0)

        # Renormalize if needed
        W_norm = np.linalg.norm(W)
        if W_norm >= 1.0:
            margin = 0.01
            W = W * (1.0 - margin) / W_norm

    return W.tolist()


def calibrate_linear_mapping(
    kappa_train: List[Dict[str, float]],
    W_train: List[List[float]]
) -> tuple:
    """
    Calibrate linear mapping A and b from training data.

    Solves: W = A·κ + b using least squares.

    Args:
        kappa_train: List of training κ dictionaries
        W_train: List of training W vectors

    Returns:
        Tuple (A, b) where A is matrix and b is intercept vector
    """
    if len(kappa_train) != len(W_train):
        raise ValueError(f"Training data size mismatch: {len(kappa_train)} vs {len(W_train)}")

    # Convert to matrices
    kappa_keys = sorted(kappa_train[0].keys())

    X = np.array([
        [k_dict.get(key, 0.0) for key in kappa_keys]
        for k_dict in kappa_train
    ], dtype=np.float64)

    Y = np.array(W_train, dtype=np.float64)

    # Add intercept column
    X_with_intercept = np.column_stack([X, np.ones(len(X))])

    # Solve: Y = X_with_intercept @ [A^T; b^T]
    # Using least squares
    coeffs = np.linalg.lstsq(X_with_intercept, Y, rcond=None)[0]

    # Extract A and b
    A = coeffs[:-1, :].T  # Shape: (7, n_params)
    b = coeffs[-1, :]     # Shape: (7,)

    return A, b


# Example usage and validation
if __name__ == "__main__":
    print("AGUA Runtime Mapping Module - Validation")
    print("=" * 50)

    # Test linear mapping
    print("\nLinear mapping test:")
    kappa = {'param1': 0.5, 'param2': 0.3, 'param3': 0.2}
    A = np.random.randn(7, 3) * 0.1
    b = np.array([0.14, 0.14, 0.14, 0.14, 0.14, 0.14, 0.16])

    W = linear_kappa_to_W(kappa, A, b)
    print(f"  κ = {kappa}")
    print(f"  W = {[f'{w:.4f}' for w in W]}")
    print(f"  ||W|| = {np.linalg.norm(W):.6f}")

    # Test kernel mapping
    print("\nKernel mapping test:")
    kappa_train = [
        {'param1': 0.4, 'param2': 0.3, 'param3': 0.3},
        {'param1': 0.5, 'param2': 0.3, 'param3': 0.2},
        {'param1': 0.6, 'param2': 0.2, 'param3': 0.2},
    ]
    W_train = [
        [0.15, 0.15, 0.14, 0.14, 0.14, 0.14, 0.14],
        [0.16, 0.15, 0.15, 0.14, 0.14, 0.13, 0.13],
        [0.17, 0.16, 0.15, 0.14, 0.13, 0.13, 0.12],
    ]

    params = {
        'kappa_train': kappa_train,
        'W_train': W_train,
        'gamma': 1.0,
        'regularization': 1e-6,
        'envelope_aware': True
    }

    W_kernel = kernel_kappa_to_W(kappa, params)
    print(f"  κ = {kappa}")
    print(f"  W = {[f'{w:.4f}' for w in W_kernel]}")
    print(f"  ||W|| = {np.linalg.norm(W_kernel):.6f}")

    # Test calibration
    print("\nLinear calibration test:")
    A_cal, b_cal = calibrate_linear_mapping(kappa_train, W_train)
    print(f"  Calibrated A shape: {A_cal.shape}")
    print(f"  Calibrated b shape: {b_cal.shape}")

    print("\n✓ All functions operational")
