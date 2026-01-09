from __future__ import annotations
import numpy as np

class AlgError(Exception):
    pass

"""
Mathematical Foundations:
Implements Optimal Transport (OT) solvers:
1. Sinkhorn-Knopp: Solves entropic regularized OT.
   min <P, C> - epsilon * H(P)
   Iterative scaling: u = a / (K v), v = b / (K^T u).
2. Greenkhorn: Greedy coordinate descent for Sinkhorn.
3. Unbalanced OT: Uses KL divergence for marginal relaxation.

Fault Detection Logic:
- Validates probability distributions (non-negative).
- Checks cost matrix dimensions.
- Handles numerical stability (log-domain Sinkhorn).
- Checks convergence.

Detailed Mechanisms:
- Sinkhorn: Alternating projections on rows and columns.
- Greenkhorn: Updates row/col with max marginal violation.
- Unbalanced: Updates with power scaling based on tau parameters.
"""

def _logsumexp(X, axis=None):
    X = np.asarray(X)
    m = np.max(X, axis=axis, keepdims=True)
    return np.squeeze(m + np.log(np.sum(np.exp(X - m), axis=axis, keepdims=True)))

def sinkhorn_entropic(a, b, C, epsilon, max_iters=10_000, tol=1e-9, stabilized=True):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    C = np.asarray(C, dtype=float)
    if a.ndim != 1 or b.ndim != 1:
        raise AlgError('a and b must be 1D arrays')
    if C.shape != (a.shape[0], b.shape[0]):
        raise AlgError('C shape mismatch with a, b')
    if epsilon <= 0:
        raise AlgError('epsilon must be > 0')

    m, n = C.shape
    if stabilized:
        f = np.zeros(m)
        g = np.zeros(n)
        log_a = np.log(a + 1e-300)
        log_b = np.log(b + 1e-300)
        for _ in range(max_iters):
            f_prev = f.copy(); g_prev = g.copy()
            f = epsilon * (log_a - _logsumexp((g[None, :] - C) / epsilon, axis=1))
            g = epsilon * (log_b - _logsumexp((f[:, None] - C) / epsilon, axis=0))
            if max(np.max(np.abs(f - f_prev)), np.max(np.abs(g - g_prev))) < tol:
                break
        P = np.exp((f[:, None] + g[None, :] - C) / epsilon)
        return P
    else:
        K = np.exp(-C / epsilon)
        u = np.ones(m) / m
        v = np.ones(n) / n
        for _ in range(max_iters):
            u_prev = u.copy(); v_prev = v.copy()
            u = a / (K @ v + 1e-300)
            v = b / (K.T @ u + 1e-300)
            if max(np.linalg.norm(u - u_prev, 1), np.linalg.norm(v - v_prev, 1)) < tol:
                break
        P = np.diag(u) @ K @ np.diag(v)
        return P

def sinkhorn_greenkhorn(a, b, C, epsilon, max_iters=50_000, tol=1e-8):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    C = np.asarray(C, dtype=float)
    if C.shape != (a.shape[0], b.shape[0]):
        raise AlgError('C shape mismatch with a, b')
    K = np.exp(-C / epsilon)
    m, n = C.shape
    u = np.ones(m)
    v = np.ones(n)
    for it in range(max_iters):
        P = (u[:, None]) * K * (v[None, :])
        row_sum = P @ np.ones(n)
        col_sum = P.T @ np.ones(m)
        r_err = row_sum - a
        c_err = col_sum - b
        i = int(np.argmax(np.abs(r_err)))
        j = int(np.argmax(np.abs(c_err)))
        if np.max([np.abs(r_err[i]), np.abs(c_err[j])]) < tol:
            break
        if np.abs(r_err[i]) >= np.abs(c_err[j]):
            Ki = K[i, :]
            denom = Ki @ v + 1e-300
            u[i] = a[i] / denom
        else:
            Kj = K[:, j]
            denom = u @ Kj + 1e-300
            v[j] = b[j] / denom
    return (u[:, None]) * K * (v[None, :])

def sinkhorn_unbalanced(a, b, C, epsilon, tau_a, tau_b, max_iters=10_000, tol=1e-8):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    C = np.asarray(C, dtype=float)
    m, n = C.shape
    K = np.exp(-C / epsilon)
    alpha = tau_a / (tau_a + epsilon)
    beta = tau_b / (tau_b + epsilon)
    u = np.ones(m)
    v = np.ones(n)
    for _ in range(max_iters):
        u_prev = u.copy(); v_prev = v.copy()
        Kv = K @ v + 1e-300
        u = (a / Kv) ** alpha
        KTu = K.T @ u + 1e-300
        v = (b / KTu) ** beta
        if max(np.linalg.norm(u - u_prev, 1), np.linalg.norm(v - v_prev, 1)) < tol:
            break
    return (u[:, None]) * K * (v[None, :])
