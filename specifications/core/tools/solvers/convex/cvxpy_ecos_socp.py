# SOCP via CVXPY using ECOS; prefer existing backend
try:
    import cvxpy as cp
    _cvxpy = cp
except Exception:
    _cvxpy = None

def solve_socp(objective_terms, constraints, params=None):
    if _cvxpy is None:
        raise NotImplementedError('cvxpy not available')
    prob = _cvxpy.Problem(_cvxpy.Minimize(objective_terms), constraints)
    prob.solve(solver=_cvxpy.ECOS)
    return {'status': prob.status, 'objective': prob.value}
