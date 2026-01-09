try:
    from relax_backend import sdp_maxcut as _sdp
except Exception:
    _sdp = None

def sdp_maxcut(G, params=None):
    if _sdp is None:
        raise NotImplementedError('relax_backend.sdp_maxcut not available')
    return _sdp(G, params=params)
