import numpy as np
from hypersync.operators.pdhg_tv_numpy import pdhg_tv_denoise

def test_tv_l1_runs():
    img = np.zeros((16,16))
    img[4:12,4:12] = 1.0
    noisy = img + 0.1*np.random.default_rng(0).normal(size=img.shape)
    out = pdhg_tv_denoise({"image": noisy, "lam": 0.2, "data_penalty": "l1", "max_iters": 30})
    assert 'x' in out and out['x'].shape == noisy.shape
