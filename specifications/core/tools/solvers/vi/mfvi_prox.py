try:
    from vi_backend import mfvi as _mfvi
except Exception:
    _mfvi = None

def mfvi(log_joint, init_q, max_iters=1000, tol=1e-6, natural_grad=True, line_search=False):
    if _mfvi is None:
        raise NotImplementedError('vi_backend.mfvi not available')
    return _mfvi(log_joint, init_q, max_iters=max_iters, tol=tol, natural_grad=natural_grad, line_search=line_search)
