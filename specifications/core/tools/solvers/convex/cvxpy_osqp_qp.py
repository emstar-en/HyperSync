# QP via CVXPY using OSQP; prefer existing backend
try:
    import cvxpy as cp
    _cvxpy = cp
except Exception:
    _cvxpy = None

try:
    from convex_backend import solve_qp as _solve_qp
except Exception:
    _solve_qp = None

def solve_qp(P, q, G=None, h=None, A=None, b=None, params=None):
    if _solve_qp is not None:
        return _solve_qp(P, q, G, h, A, b, params=params)
    if _cvxpy is None:
        raise NotImplementedError('cvxpy or convex_backend.solve_qp not available')
    # Minimal CVXPY QP solver skeleton
    x = _cvxpy.Variable(len(q))
    obj = 0.5*_cvxpy.quad_form(x, P) + q @ x
    constr = []
    if G is not None and h is not None:
        constr.append(G @ x <= h)
    if A is not None and b is not None:
        constr.append(A @ x == b)
    prob = _cvxpy.Problem(_cvxpy.Minimize(obj), constr)
    kwargs = {}
    if params and isinstance(params, dict):
        kwargs['max_iters'] = params.get('max_iters')
    prob.solve(solver=_cvxpy.OSQP, **kwargs)
    return {'x': x.value, 'status': prob.status, 'objective': prob.value}
