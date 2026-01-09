import numpy as np
from hypersync.operators.pdhg_numpy import pdhg_solve

def test_pdhg_elastic_net_runs():
    rng = np.random.default_rng(0)
    A = rng.normal(size=(20,10))
    x_true = rng.normal(size=10)
    b = A @ x_true + 0.01 * rng.normal(size=20)
    params = dict(A=A, b=b, lam=0.1, lam1=0.1, lam2=0.05, penalty='elastic_net', tau=0.5, sigma=0.5, max_iters=50)
    out = pdhg_solve(params)
    assert 'x' in out and out['iters'] <= 50
