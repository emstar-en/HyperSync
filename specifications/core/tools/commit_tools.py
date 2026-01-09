import hashlib, json

def canonical_json_hash(obj) -> str:
    def _norm(x):
        if isinstance(x, dict):
            return {k: _norm(x[k]) for k in sorted(x)}
        if isinstance(x, list):
            return [_norm(v) for v in x]
        return x
    norm = _norm(obj)
    data = json.dumps(norm, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return 'sha256:' + hashlib.sha256(data).hexdigest()
