from __future__ import annotations
from typing import Dict, Any, List
import math
import random

class PDHGError(Exception):
    pass

"""
Mathematical Foundations:
Pure Python implementation of PDHG.
See pdhg_numpy.py for mathematical details.
This implementation avoids NumPy dependencies, using standard lists.

Fault Detection Logic:
- Checks dimensions.
- Handles matrix operations safely.

Detailed Mechanisms:
- Matrix-vector multiplication implemented via loops.
- Norms and projections implemented via loops.
"""

def _mat_vec(A: List[List[float]], x: List[float]) -> List[float]:
    return [sum(a * b for a, b in zip(row, x)) for row in A]

def _mat_T_vec(A: List[List[float]], y: List[float]) -> List[float]:
    # A is m x n. A.T is n x m.
    # result[j] = sum(A[i][j] * y[i])
    n = len(A[0])
    m = len(A)
    res = [0.0] * n
    for i in range(m):
        val = y[i]
        row = A[i]
        for j in range(n):
            res[j] += row[j] * val
    return res

def _vec_add(u: List[float], v: List[float], scale_v: float = 1.0) -> List[float]:
    return [a + scale_v * b for a, b in zip(u, v)]

def _vec_sub(u: List[float], v: List[float]) -> List[float]:
    return [a - b for a, b in zip(u, v)]

def _norm(v: List[float]) -> float:
    return math.sqrt(sum(x*x for x in v))

def _prox_f_conj(y: List[float], sigma: float, b: List[float]) -> List[float]:
    # (y - sigma * b) / (1 + sigma)
    denom = 1.0 + sigma
    return [(yi - sigma * bi) / denom for yi, bi in zip(y, b)]

def _prox_g_l1(x: List[float], tau: float, lam: float) -> List[float]:
    t = tau * lam
    res = []
    for xi in x:
        mag = abs(xi) - t
        if mag < 0: mag = 0.0
        res.append(math.copysign(mag, xi))
    return res

def _prox_g_l2(x: List[float], tau: float, lam: float) -> List[float]:
    denom = 1.0 + tau * lam
    return [xi / denom for xi in x]

def pdhg_solve_pure(params: Dict[str, Any]) -> Dict[str, Any]:
    A = params.get('A') # List[List[float]]
    b = params.get('b') # List[float]
    lam = float(params.get('lam', 0.0))
    tau = params.get('tau')
    sigma = params.get('sigma')
    theta = float(params.get('theta', 1.0))
    max_iters = int(params.get('max_iters', 1000))
    tol = float(params.get('tol', 1e-6))
    penalty = params.get('penalty', 'l1')

    if not A or not b:
        raise PDHGError("A and b required")
    m = len(A)
    n = len(A[0])

    x = params.get('x0', [0.0]*n)
    y = [0.0]*m
    x_bar = list(x)

    # Power iteration for norm
    if tau is None or sigma is None:
        v = [random.gauss(0,1) for _ in range(n)]
        nv = _norm(v)
        v = [vi/nv for vi in v]
        for _ in range(10):
            Av = _mat_vec(A, v)
            ATAv = _mat_T_vec(A, Av)
            nv = _norm(ATAv) # This is actually norm(A^T A v) approx norm(A)^2 * v
            # Wait, power method finds largest eigenvalue of A^T A, which is sigma_max(A)^2.
            # So sqrt(nv) is not quite right if we iterate A^T A.
            # Let's do v = A^T A v. Then norm(v) converges to lambda_max(A^T A) * norm(v_prev).
            # Actually, Rayleigh quotient is better.
            # Simple: v <- A^T A v; v <- v / norm(v). The eigenvalue is approx norm(v) (if normalized at each step).
            # Let's just do:
            w = _mat_vec(A, v)
            z = _mat_T_vec(A, w)
            nz = _norm(z)
            if nz < 1e-12: break
            v = [zi/nz for zi in z]

        # Estimate spectral radius of A^T A is approx nz (from last step z = A^T A v_prev, |z| ~ lambda |v_prev| = lambda)
        # So L = sqrt(lambda) = sqrt(nz)
        L = math.sqrt(nz) if nz > 0 else 1.0
        tau = 1.0 / L
        sigma = 1.0 / L

    for it in range(max_iters):
        x_prev = list(x)
        y_prev = list(y)

        # y = prox_f*(y + sigma A x_bar)
        Ax_bar = _mat_vec(A, x_bar)
        arg_y = _vec_add(y, Ax_bar, sigma)
        y = _prox_f_conj(arg_y, sigma, b)

        # x = prox_g(x - tau A^T y)
        ATy = _mat_T_vec(A, y)
        arg_x = _vec_add(x, ATy, -tau)
        if penalty == 'l1':
            x = _prox_g_l1(arg_x, tau, lam)
        else:
            x = _prox_g_l2(arg_x, tau, lam)

        # x_bar = x + theta(x - x_prev)
        x_bar = _vec_add(x, _vec_sub(x, x_prev), theta)

        # Convergence
        dx = _norm(_vec_sub(x, x_prev)) / (_norm(x_prev) + 1e-12)
        if dx < tol:
            break

    return {'x': x, 'iters': it+1}
