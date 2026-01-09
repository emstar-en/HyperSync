# Delta tools that prefer existing backends if available
try:
    from delta_backend import apply_delta as _apply_delta
except Exception:
    _apply_delta = None

try:
    from delta_backend import revoke_delta as _revoke_delta
except Exception:
    _revoke_delta = None


def apply_delta(doc, delta_ops):
    if _apply_delta is None:
        raise NotImplementedError('delta_backend.apply_delta not available')
    return _apply_delta(doc, delta_ops)


def revoke_delta(state, delta_id, reason):
    if _revoke_delta is None:
        raise NotImplementedError('delta_backend.revoke_delta not available')
    return _revoke_delta(state, delta_id, reason)
