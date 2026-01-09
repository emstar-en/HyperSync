try:
    from prox_backend import pdhg as _pdhg
except Exception:
    _pdhg = None

def pdhg(grad_terms, prox_terms, tau, sigma, theta=1.0, max_iters=1000, tol=1e-6):
    if _pdhg is None:
        raise NotImplementedError('prox_backend.pdhg not available')
    return _pdhg(grad_terms, prox_terms, tau, sigma, theta=theta, max_iters=max_iters, tol=tol)
