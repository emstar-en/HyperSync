import numpy as np
from hypersync.engine.runtime import Runtime

def test_geodesic_fallback(tmp_path):
    spec_root = tmp_path / 'spec_pack'
    spec_root.mkdir()
    rt = Runtime(spec_root)
    intent = {
        "id": "g1",
        "op": "op://geodesic_fast_marching.0",
        "params": {"index_of_refraction": [[1,1,1],[1,2,1],[1,1,1]], "sources": [[1,1]]},
        "meta": {"tier":"core"}
    }
    rec = rt.run_intent(intent)
    assert rec['status'] == 'OK'
    D = np.array(rec['outputs']['eikonal_solution']['distance'])
    assert D.shape == (3,3)
    assert np.isfinite(D).all()
