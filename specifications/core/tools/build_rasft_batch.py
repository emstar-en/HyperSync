import json, argparse, pathlib, uuid, time

    def build_example(q, passages):
        # Trivial: answer echoes first passage, cites its address
        addr = passages[0]['content_address']
        text = passages[0]['text']
        ans = f"According to {addr}: {text[:200]}"
        return {
            'input': {'query': q, 'passages': [p['text'] for p in passages[:5]]},
            'output': {'answer': ans, 'citations': [addr]},
            'meta': {'addresses': [p['content_address'] for p in passages], 'as_of': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
        }

    def main():
        ap = argparse.ArgumentParser()
        
        add_common_args(ap)
ap.add_argument('--queries', required=False)
        ap.add_argument('--retrieval', required=False)
        ap.add_argument('--out', required=True)
        args = ap.parse_args()

        
        _envelope_op = load_envelope_op(args)
# Read queries (one per line) and retrieval (JSON lines with {query, passages:[{text,content_address}]})
        queries = []
        if args.queries and pathlib.Path(args.queries).exists():
            queries = [l.strip() for l in pathlib.Path(args.queries).read_text(encoding='utf-8').splitlines() if l.strip()]
        items = []
        if args.retrieval and pathlib.Path(args.retrieval).exists():
            for line in pathlib.Path(args.retrieval).read_text(encoding='utf-8').splitlines():
                if not line.strip(): continue
                obj = json.loads(line)
                q = obj.get('query') or (queries[0] if queries else 'unknown')
                passages = obj.get('passages') or []
                if not passages: continue
                items.append(build_example(q, passages))
        else:
            # fallback: synthetic passage
            items.append(build_example('what is hypersync?', [{'text':'HyperSync is a geometry-native orchestration layer.','content_address':'addr://doc/synthetic#1'}]))

        outp = pathlib.Path(args.out)
        outp.parent.mkdir(parents=True, exist_ok=True)
        with outp.open('w', encoding='utf-8') as f:
            for it in items:
                f.write(json.dumps(it, ensure_ascii=False)+'
')
        print(json.dumps({'ok': True, 'wrote': len(items), 'path': str(outp)}))

    if __name__ == '__main__':
        main()
