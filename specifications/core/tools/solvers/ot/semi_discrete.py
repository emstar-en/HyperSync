try:
    from ot_backend import semi_discrete as _sd
except Exception:
    _sd = None

def semi_discrete(source, target, params=None):
    if _sd is None:
        raise NotImplementedError('ot_backend.semi_discrete not available')
    return _sd(source, target, params=params)
