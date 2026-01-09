import json
from pathlib import Path
from hypersync.engine.runtime import Runtime

def test_plan_falls_back_to_builtin(tmp_path):
    spec_root = tmp_path / 'spec_pack'
    (spec_root / 'planner' / 'routing').mkdir(parents=True, exist_ok=True)
    # empty rules -> use builtin
    (spec_root / 'planner' / 'routing' / 'geometric_unified.rules.json').write_text(json.dumps({}))
    rt = Runtime(spec_root)
    intent = {"op": "task://optimal_transport", "params": {"a":[0.5,0.5],"b":[0.5,0.5],"C":[[0,1],[1,0]],"epsilon":0.1}}
    rcpt = rt.run_intent(intent)
    assert rcpt.op.endswith('sinkhorn_entropic.0')
    assert rcpt.status == 'OK'
