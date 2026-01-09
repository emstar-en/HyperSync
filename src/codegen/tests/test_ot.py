import numpy as np
from hypersync.engine.runtime import Runtime

def test_sinkhorn_entropic_fallback(tmp_path):
    spec_root = tmp_path / 'spec_pack'
    spec_root.mkdir()
    rt = Runtime(spec_root)
    intent = {
        "id": "t1",
        "op": "op://sinkhorn_entropic.0",
        "params": {
            "a": [0.5,0.5],
            "b": [0.3,0.7],
            "C": [[0.0,1.0],[1.0,0.0]],
            "epsilon": 0.1
        },
        "meta": {"tier":"core"}
    }
    rec = rt.run_intent(intent)
    assert rec['status'] == 'OK'
    P = np.array(rec['outputs']['transport_plan'])
    assert P.shape == (2,2)
