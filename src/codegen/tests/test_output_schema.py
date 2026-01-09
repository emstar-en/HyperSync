import json
from hypersync.engine.runtime import Runtime

def test_output_schema_validation(tmp_path):
    spec_root = tmp_path / 'spec_pack'
    opdir = spec_root / 'operators'
    opdir.mkdir(parents=True, exist_ok=True)
    meta = {
        "id": "op://sinkhorn_entropic.0",
        "output_schema": {
            "type": "object",
            "required": ["transport_plan"],
            "properties": {"transport_plan": {"type": "array"}}
        }
    }
    (opdir / 'op_sinkhorn_entropic_v1.0.json').write_text(json.dumps(meta))
    rt = Runtime(spec_root)
    intent = {"op": "op://sinkhorn_entropic.0", "params": {"a":[0.5,0.5],"b":[0.5,0.5],"C":[[0,1],[1,0]],"epsilon":0.1}}
    rcpt = rt.run_intent(intent)
    assert rcpt.status == 'OK'
