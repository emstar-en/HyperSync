#!/usr/bin/env python3
import json, sys
from pathlib import Path

PRETTY = True
SORT_KEYS = True


def to_json_bytes(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=SORT_KEYS).encode('utf-8')


def load_json(p: Path):
    return json.loads(p.read_text(encoding='utf-8'))


def deep_merge_dict(a: dict, b: dict):
    for k, v in b.items():
        if k in a and isinstance(a[k], dict) and isinstance(v, dict):
            deep_merge_dict(a[k], v)
        else:
            a[k] = v
    return a


def main():
    pack_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('reconstructed.json')
    index_path = pack_root / 'spec.index.json'
    idx = load_json(index_path)

    doc = {}
    for comp in idx.get('components', []):
        key = comp['target_key']
        mode = comp.get('merge', 'object')
        if mode == 'object':
            if key not in doc or not isinstance(doc.get(key), dict):
                doc[key] = {}
            for rel in comp['files']:
                part = load_json(pack_root / rel)
                if not isinstance(part, dict):
                    raise TypeError(f"Expected dict for component {key} in {rel}")
                deep_merge_dict(doc[key], part)
        elif mode == 'array_concat':
            if key not in doc or not isinstance(doc.get(key), list):
                doc[key] = []
            for rel in comp['files']:
                part = load_json(pack_root / rel)
                if not isinstance(part, list):
                    raise TypeError(f"Expected list for component {key} in {rel}")
                doc[key].extend(part)
        elif mode == 'replace':
            # last one wins
            for rel in comp['files']:
                part = load_json(pack_root / rel)
                doc[key] = part
        else:
            raise ValueError(f"Unknown merge mode: {mode} for key {key}")

    out_path.write_bytes(to_json_bytes(doc))
    print(f"Wrote {out_path} with {len(doc)} top-level keys.")

if __name__ == '__main__':
    main()
