import numpy as np
from hypersync.engine.runtime import Runtime

def test_pdhg_tv_denoise(tmp_path):
    spec_root = tmp_path / 'spec_pack'
    spec_root.mkdir()
    rt = Runtime(spec_root)
    img = [[0,0,0,0,0],[0,1,1,1,0],[0,1,1,1,0],[0,1,1,1,0],[0,0,0,0,0]]
    intent = {
        "id": "tv1",
        "op": "op://pdhg_tv_denoise.0",
        "params": {"image": img, "lam": 0.2, "max_iters": 50},
        "meta": {"tier":"core"}
    }
    rec = rt.run_intent(intent)
    assert rec['status'] == 'OK'
    den = np.array(rec['outputs']['denoised']['x'])
    assert den.shape == (5,5)
    assert den.max() <= 1.0 + 1e-6 and den.min() >= -1e-6
