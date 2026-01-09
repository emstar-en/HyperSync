try:
    from relax_backend import mccormick as _mc
except Exception:
    _mc = None

def mccormick(bilinear_terms, bounds_policy=None, tightening_iters=0):
    if _mc is None:
        raise NotImplementedError('relax_backend.mccormick not available')
    return _mc(bilinear_terms, bounds_policy=bounds_policy, tightening_iters=tightening_iters)
