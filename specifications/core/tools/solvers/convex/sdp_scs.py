# SDP via CVXPY SCS; prefer existing backend
try:
    import cvxpy as cp
    _cvxpy = cp
except Exception:
    _cvxpy = None

def solve_sdp(X_constraints, objective, params=None):
    if _cvxpy is None:
        raise NotImplementedError('cvxpy not available')
    prob = _cvxpy.Problem(_cvxpy.Minimize(objective), X_constraints)
    prob.solve(solver=_cvxpy.SCS)
    return {'status': prob.status, 'objective': prob.value}
