import json
from pathlib import Path
from hypersync.engine.runtime import Runtime

def test_required_params_enforced(tmp_path):
    spec_root = tmp_path / 'spec_pack'
    opdir = spec_root / 'operators'
    opdir.mkdir(parents=True, exist_ok=True)
    # simple operator metadata with required param list
    meta = {"id": "op://dummy.0", "params": {"required": ["alpha", "beta"]}}
    (opdir / 'op_dummy.json').write_text(json.dumps(meta))
    rt = Runtime(spec_root)
    # missing beta -> should fail
    intent = {"op": "op://dummy.0", "params": {"alpha": 1}}
    rcpt = rt.run_intent(intent)
    assert rcpt.status == 'FAIL'
    assert rcpt.outputs.get('error') == 'InvalidParameters'
