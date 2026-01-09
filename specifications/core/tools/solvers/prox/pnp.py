try:
    from prox_backend import pnp as _pnp
except Exception:
    _pnp = None

def pnp(denoiser_ref, sigma, max_iters=1000, tol=1e-6, seed=None):
    if _pnp is None:
        raise NotImplementedError('prox_backend.pnp not available')
    return _pnp(denoiser_ref, sigma, max_iters=max_iters, tol=tol, seed=seed)
