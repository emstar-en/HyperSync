import argparse, json, pathlib, time, hashlib
try:
    from cli_common import add_common_args, load_envelope_op
except Exception:
    def add_common_args(ap):
        return ap
    def load_envelope_op(args):
        return None


    def now_ms():
        return int(time.time()*1000)

    def h(s: bytes):
        import hashlib
        return hashlib.sha256(s).hexdigest()

    def main():
        ap = argparse.ArgumentParser()
        ap.add_argument('--out_dir', required=True)
        ap.add_argument('--key', required=True)
        ap.add_argument('--value', required=True)
        ap.add_argument('--type', dest='vtype', default='routing_prior')
        ap.add_argument('--ttl_ms', type=int, default=3600000)
        ap.add_argument('--mode', choices=['pointer_only','payload_redacted','payload_encrypted'], default='pointer_only')
        args = ap.parse_args()
        out = pathlib.Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)
        rec = {
            'k': args.key,
            't': now_ms(),
            'ttl_ms': args.ttl_ms,
            'type': args.vtype,
            'mode': args.mode,
            'val': args.value if args.mode!='payload_redacted' else f'hash:{h(args.value.encode())}'
        }
        (out/'mem.jsonl').open('a', encoding='utf-8').write(json.dumps(rec, ensure_ascii=False)+'
')
        print(json.dumps({'ok': True, 'wrote': 1}))

    if __name__ == '__main__':
        main()
