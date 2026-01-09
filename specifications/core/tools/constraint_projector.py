# Constraint projector stub (e.g., project to div-free space)
try:
    from constraints_backend import project as _project
except Exception:
    _project = None

def project(state, constraints):
    if _project is None:
        raise NotImplementedError('constraint projector backend not available')
    return _project(state, constraints)
