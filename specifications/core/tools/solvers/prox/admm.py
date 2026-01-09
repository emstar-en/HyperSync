try:
    from prox_backend import admm as _admm
except Exception:
    _admm = None

def admm(primal_ops, dual_ops, rho=1.0, max_iters=1000, abs_tol=1e-5, rel_tol=1e-4):
    if _admm is None:
        raise NotImplementedError('prox_backend.admm not available')
    return _admm(primal_ops, dual_ops, rho=rho, max_iters=max_iters, abs_tol=abs_tol, rel_tol=rel_tol)
