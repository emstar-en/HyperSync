# DEC operator facade; reuses existing operators if available
try:
    from exterior_derivative import exterior_derivative  # existing module?
except Exception:
    def exterior_derivative(form):
        raise NotImplementedError('exterior_derivative not available')

try:
    from hodge import hodge_star  # existing module?
except Exception:
    def hodge_star(form, metric):
        raise NotImplementedError('hodge_star not available')

try:
    from wedge import wedge  # existing module?
except Exception:
    def wedge(a, b):
        raise NotImplementedError('wedge not available')
