from __future__ import annotations
import numpy as np
from typing import Dict, Any

class PDHGError(Exception):
    pass

"""
Mathematical Foundations:
The Primal-Dual Hybrid Gradient (PDHG) algorithm, also known as the Chambolle-Pock algorithm, solves saddle-point problems of the form:
    min_x max_y <Ax, y> + g(x) - f*(y)
where f and g are convex functions.
The update steps are:
    y_{k+1} = prox_{sigma f*}(y_k + sigma A x_bar_k)
    x_{k+1} = prox_{tau g}(x_k - tau A^T y_{k+1})
    x_bar_{k+1} = x_{k+1} + theta (x_{k+1} - x_k)

Convergence is guaranteed if tau * sigma * ||A||^2 < 1.

Fault Detection Logic:
- Validates dimensions of A and b.
- Checks for valid penalty types.
- Monitors convergence via primal and dual residuals.
- Safely computes spectral norm for step size selection, falling back to defaults if estimation fails.

Detailed Mechanisms:
1. Initialize x, y, x_bar.
2. Estimate Lipschitz constant L = ||A|| via power iteration to set step sizes tau, sigma.
3. Iterate:
    a. Update dual variable y using prox of conjugate f*.
    b. Update primal variable x using prox of g (L1, L2, or Elastic Net).
    c. Update relaxation x_bar.
    d. Check convergence criteria.
4. Return solution and diagnostics.
"""

def _prox_f_conj(y, sigma, b):
    return (y - sigma * b) / (1.0 + sigma)

def _prox_g_l1(x, tau, lam):
    t = tau * lam
    return np.sign(x) * np.maximum(np.abs(x) - t, 0.0)

def _prox_g_l2(x, tau, lam):
    return x / (1.0 + tau * lam)

def _prox_g_elastic(x, tau, lam1, lam2):
    denom = 1.0 + tau * lam2
    u = x / denom
    t = (tau * lam1) / denom
    return np.sign(u) * np.maximum(np.abs(u) - t, 0.0)

def pdhg_solve(params: Dict[str, Any]) -> Dict[str, Any]:
    A = np.asarray(params.get('A'), dtype=float)
    b = np.asarray(params.get('b'), dtype=float)
    lam = float(params.get('lam', 0.0))
    tau = params.get('tau')
    sigma = params.get('sigma')
    theta = float(params.get('theta', 1.0))
    max_iters = int(params.get('max_iters', 1000))
    tol = float(params.get('tol', 1e-6))

    preset = params.get('preset')
    penalty = params.get('penalty')
    if preset == 'ridge':
        penalty = 'l2'
    elif preset == 'lasso':
        penalty = 'l1'
    elif preset == 'elastic_net':
        penalty = 'elastic_net'

    if penalty not in ('l1', 'l2', 'elastic_net', None):
        raise PDHGError('penalty must be one of l1, l2, elastic_net')
    if penalty is None:
        penalty = 'l1'

    if A.ndim != 2:
        raise PDHGError('A must be 2D')
    m, n = A.shape
    if b.shape != (m,):
        raise PDHGError('b shape must be (m,) with m = A.shape[0]')

    x = np.asarray(params.get('x0', np.zeros(n)), dtype=float)
    y = np.zeros(m)
    x_bar = x.copy()

    AT = A.T

    # Step size safety: tau*sigma*||A||^2 < 1
    if tau is None or sigma is None:
        def _power_norm(A, iters=20):
            try:
                v = np.random.randn(A.shape[1])
                v /= (np.linalg.norm(v) + 1e-15)
                for _ in range(iters):
                    v = A.T @ (A @ v)
                    nv = np.linalg.norm(v) + 1e-15
                    v /= nv
                return np.sqrt(nv)
            except Exception:
                return 1.0 # Fallback

        normA = _power_norm(A)
        # Default step sizes
        L = normA
        if L < 1e-12: L = 1.0
        tau = 1.0 / L
        sigma = 1.0 / L

    if penalty == 'l1':
        prox_g = _prox_g_l1
    elif penalty == 'l2':
        prox_g = _prox_g_l2
    else:
        lam1 = float(params.get('lam1', lam))
        lam2 = float(params.get('lam2', 0.0))
        prox_g = lambda x, tau, _lam_ignored: _prox_g_elastic(x, tau, lam1, lam2)

    for it in range(max_iters):
        y_prev = y.copy()
        x_prev = x.copy()

        y = _prox_f_conj(y + sigma * (A @ x_bar), sigma, b)
        x = prox_g(x - tau * (AT @ y), tau, lam)
        x_bar = x + theta * (x - x_prev)

        r_pri = np.linalg.norm(x - x_prev) / (np.linalg.norm(x_prev) + 1e-12)
        r_dual = np.linalg.norm(y - y_prev) / (np.linalg.norm(y_prev) + 1e-12)
        if max(r_pri, r_dual) < tol:
            break

    if penalty == 'l1':
        reg = lam * np.sum(np.abs(x))
    else:
        reg = 0.5 * lam * np.sum(x * x)
    obj = 0.5 * np.linalg.norm(A @ x - b) ** 2 + reg
    return { 'x': x, 'objective': float(obj), 'iters': it+1, 'penalty': penalty }
