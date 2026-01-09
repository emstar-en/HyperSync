try:
    from ot_backend import sinkhorn as _sinkhorn
except Exception:
    _sinkhorn = None

def sinkhorn(a, b, C, epsilon, max_iters=10000, tol=1e-9, stabilized=True):
    if _sinkhorn is None:
        raise NotImplementedError('ot_backend.sinkhorn not available')
    return _sinkhorn(a, b, C, epsilon, max_iters=max_iters, tol=tol, stabilized=stabilized)
