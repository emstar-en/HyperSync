# JKO proximal step placeholder; prefer existing optimal-transport backend
try:
    from ot_backend import jko_step as _jko
except Exception:
    _jko = None

def jko_step(rho, tau, energy):
    if _jko is None:
        raise NotImplementedError('JKO backend not available')
    return _jko(rho, tau, energy)
