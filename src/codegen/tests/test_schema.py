import json
from hypersync.engine.runtime import Runtime

def test_operator_schema_inline(tmp_path):
    spec_root = tmp_path / 'spec_pack'
    opdir = spec_root / 'operators'
    opdir.mkdir(parents=True, exist_ok=True)
    # simple jsonschema inline
    meta = {
        "id": "op://schema_test.0",
        "input_schema": {
            "type": "object",
            "properties": {"alpha": {"type": "number"}},
            "required": ["alpha"]
        }
    }
    (opdir / 'op_schema_test.json').write_text(json.dumps(meta))
    rt = Runtime(spec_root)
    # missing alpha -> fail
    rcpt = rt.run_intent({"op": "op://schema_test.0", "params": {}})
    assert rcpt.status == 'FAIL'
    # valid -> ok (executor has no mapping; expect failure before exec)
