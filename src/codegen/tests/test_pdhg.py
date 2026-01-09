import numpy as np
from hypersync.engine.runtime import Runtime

def test_pdhg_lasso_fallback(tmp_path):
    spec_root = tmp_path / 'spec_pack'
    spec_root.mkdir()
    rt = Runtime(spec_root)
    A = [[1,0],[0,1],[1,1]]
    b = [1,2,2.8]
    intent = {
        "id": "p1",
        "op": "op://pdhg.0",
        "params": {
            "A": A, "b": b, "lam": 0.1,
            "tau": 0.5, "sigma": 0.5, "max_iters": 200
        },
        "meta": {"tier":"core"}
    }
    rec = rt.run_intent(intent)
    assert rec['status'] == 'OK'
    x = np.array(rec['outputs']['solution']['x'])
    assert x.shape == (2,)
