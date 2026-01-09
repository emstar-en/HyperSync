try:
    from vi_backend import laplace_newton as _laplace
except Exception:
    _laplace = None

def laplace_newton(log_post, x0, max_newton_iters=50, hessian_reg=1e-6, tol=1e-6):
    if _laplace is None:
        raise NotImplementedError('vi_backend.laplace_newton not available')
    return _laplace(log_post, x0, max_newton_iters=max_newton_iters, hessian_reg=hessian_reg, tol=tol)
