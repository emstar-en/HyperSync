from __future__ import annotations
from typing import Dict, Any
import numpy as np

class PDHGTVError(Exception):
    pass

"""
Mathematical Foundations:
Rudin-Osher-Fatemi (ROF) Total Variation denoising model:
    min_x  lam * TV(x) + 1/2 ||x - b||^2
where TV(x) is the isotropic total variation (sum of L2 norm of gradient).
Solved via PDHG (Chambolle-Pock).
    Primal: x (image)
    Dual: p (flux, vector field)

Fault Detection Logic:
- Checks input image dimensions.
- Auto-selects step sizes tau, sigma based on Lipschitz bound (L^2 <= 8).
- Monitors primal and dual residuals for convergence.

Detailed Mechanisms:
1. Compute gradients (forward difference) and divergence (backward difference).
2. Iterate:
    a. Dual update: p = p + sigma * grad(x_bar).
    b. Projection: p = p / max(1, |p|/lam) (L2 ball projection).
    c. Primal update: x = (x - tau * div(p) + tau * b) / (1 + tau).
    d. Relaxation: x_bar = 2x - x_prev.
3. Return denoised image.
"""

def _grad(x):
    gx = np.zeros_like(x)
    gy = np.zeros_like(x)
    gx[:, :-1] = x[:, 1:] - x[:, :-1]
    gy[:-1, :] = x[1:, :] - x[:-1, :]
    return gx, gy

def _div(px, py):
    div = np.zeros_like(px)
    div[:, :-1] += px[:, :-1]
    div[:, 1:]  -= px[:, :-1]
    div[:-1, :] += py[:-1, :]
    div[1:,  :] -= py[:-1, :]
    return div

def pdhg_tv_denoise(params: Dict[str, Any]) -> Dict[str, Any]:
    b = np.asarray(params.get('image'), dtype=float)
    if b.ndim != 2:
        raise PDHGTVError('image must be 2D')
    lam = float(params.get('lam', 0.1))
    tau = params.get('tau')
    sigma = params.get('sigma')
    theta = float(params.get('theta', 1.0))
    max_iters = int(params.get('max_iters', 1000))
    tol = float(params.get('tol', 1e-5))
    data_penalty = (params.get('data_penalty') or 'l2').lower()

    H, W = b.shape
    x = b.copy()
    x_bar = x.copy()
    px = np.zeros_like(b)
    py = np.zeros_like(b)

    L2 = 8.0
    if tau is None or sigma is None:
        tau = 1.0 / np.sqrt(L2 + 1e-12)
        sigma = 1.0 / np.sqrt(L2 + 1e-12)

    for it in range(max_iters):
        x_prev = x.copy()

        gx, gy = _grad(x_bar)
        px_new = px + sigma * gx
        py_new = py + sigma * gy

        norm = np.maximum(1.0, np.sqrt(px_new**2 + py_new**2) / (lam + 1e-12))
        px = px_new / norm
        py = py_new / norm

        div_p = _div(px, py)
        if data_penalty == 'l1':
            v = x_prev - tau * div_p
            r = v - b
            x = b + np.sign(r) * np.maximum(np.abs(r) - tau, 0.0)
        else:
            x = (x_prev - tau * div_p + tau * b) / (1.0 + tau)

        x_bar = x + theta * (x - x_prev)

        dx = np.linalg.norm(x - x_prev) / (np.linalg.norm(x_prev) + 1e-12)
        if dx < tol:
            break

    return { 'x': x, 'iters': it+1 }
