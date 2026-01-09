import os, json
from hypersync.engine.runtime import Runtime

def test_artifacts_env(tmp_path, monkeypatch):
    monkeypatch.setenv('HYPERSYNC_ARTIFACTS_DIR', str(tmp_path/'arts'))
    spec_root = tmp_path / 'spec_pack'
    spec_root.mkdir()
    rt = Runtime(spec_root)
    intent = {"op": "task://optimal_transport", "params": {"a":[0.5,0.5],"b":[0.5,0.5],"C":[[0,1],[1,0]],"epsilon":0.1}}
    rcpt = rt.run_intent(intent)
    assert rcpt.status == 'OK'
    # artifacts dir should be created and have subdirs
    arts = tmp_path/'arts'
    assert arts.exists()
