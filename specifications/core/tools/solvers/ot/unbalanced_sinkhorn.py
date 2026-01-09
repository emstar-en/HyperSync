try:
    from ot_backend import unbalanced_sinkhorn as _us
except Exception:
    _us = None

def unbalanced_sinkhorn(a, b, C, tau_source, tau_target, epsilon, max_iters=10000):
    if _us is None:
        raise NotImplementedError('ot_backend.unbalanced_sinkhorn not available')
    return _us(a, b, C, tau_source, tau_target, epsilon, max_iters=max_iters)
