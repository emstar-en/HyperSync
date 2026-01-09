import argparse, json, pathlib, time
try:
    from cli_common import add_common_args, load_envelope_op
except Exception:
    def add_common_args(ap):
        return ap
    def load_envelope_op(args):
        return None


    def main():
        ap = argparse.ArgumentParser()
        ap.add_argument('--in', dest='inp', required=True)
        ap.add_argument('--out', dest='out', required=True)
        ap.add_argument('--ttl_ms', type=int, required=True)
        ap.add_argument('--dry_run', action='store_true')
        args = ap.parse_args()
        inp = pathlib.Path(args.inp)
        out = pathlib.Path(args.out); out.mkdir(parents=True, exist_ok=True)
        now = int(time.time()*1000)
        kept = 0
        merged = {}
        src = inp/'mem.jsonl'
        if not src.exists():
            print(json.dumps({'ok': True, 'kept': 0, 'note': 'no input'})); return
        for line in src.read_text(encoding='utf-8').splitlines():
            if not line.strip(): continue
            rec = json.loads(line)
            if now - rec.get('t', now) > args.ttl_ms:
                continue
            k = (rec.get('type',''), rec.get('k',''))
            merged[k] = rec  # keep last-writer-wins
        if not args.dry_run:
            with (out/'mem_compacted.jsonl').open('w', encoding='utf-8') as f:
                for (t,k), rec in merged.items():
                    f.write(json.dumps(rec, ensure_ascii=False)+'
')
        print(json.dumps({'ok': True, 'kept': len(merged)}))

    if __name__ == '__main__':
        main()
