try:
    from vi_backend import ep_fixed_point as _ep
except Exception:
    _ep = None

def ep_fixed_point(sites, max_iters=1000, damping=0.5, moment_matching='deterministic'):
    if _ep is None:
        raise NotImplementedError('vi_backend.ep_fixed_point not available')
    return _ep(sites, max_iters=max_iters, damping=damping, moment_matching=moment_matching)
