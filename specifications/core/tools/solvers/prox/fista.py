# FISTA skeleton; prefer prox_backend.fista
try:
    from prox_backend import fista as _fista
except Exception:
    _fista = None

def fista(grad_f, prox_g, x0, step_size='backtracking', max_iters=1000, tol=1e-6, momentum=True):
    if _fista is None:
        raise NotImplementedError('prox_backend.fista not available')
    return _fista(grad_f, prox_g, x0, step_size=step_size, max_iters=max_iters, tol=tol, momentum=momentum)
