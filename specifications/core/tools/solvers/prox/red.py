try:
    from prox_backend import red as _red
except Exception:
    _red = None

def red(lambda_, denoiser_ref, step_size=1.0, max_iters=1000, tol=1e-6):
    if _red is None:
        raise NotImplementedError('prox_backend.red not available')
    return _red(lambda_, denoiser_ref, step_size=step_size, max_iters=max_iters, tol=tol)
