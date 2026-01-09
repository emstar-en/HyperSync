import os, json, tempfile
from hypersync.engine.runtime import Runtime

def test_sign_and_verify(tmp_path, monkeypatch):
    spec_root = tmp_path / 'spec_pack'
    spec_root.mkdir()
    rt = Runtime(spec_root)
    intent = {
        "id": "sig1",
        "op": "op://sinkhorn_entropic.0",
        "params": {"a":[0.5,0.5],"b":[0.3,0.7],"C":[[0,1],[1,0]],"epsilon":0.1},
        "meta": {"tier":"core"}
    }
    # without secret
    rcpt = rt.run_intent(intent)
    assert rcpt.signature is None
    # with secret env
    monkeypatch.setenv('HYPERSYNC_HMAC_SECRET','abc123')
    rcpt = rt.run_intent(intent)
    assert rcpt.signature is not None
