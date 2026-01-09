try:
    from relax_backend import lp_mip_relax as _lp
except Exception:
    _lp = None

def lp_mip_relax(model, cut_policy=None, gap_tolerance=None, time_budget_ms=None):
    if _lp is None:
        raise NotImplementedError('relax_backend.lp_mip_relax not available')
    return _lp(model, cut_policy=cut_policy, gap_tolerance=gap_tolerance, time_budget_ms=time_budget_ms)
