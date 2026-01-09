import argparse, pathlib, hashlib
try:
    from cli_common import add_common_args, load_envelope_op
except Exception:
    def add_common_args(ap):
        return ap
    def load_envelope_op(args):
        return None


        def sha256_file(p):
            h = hashlib.sha256()
            with open(p, 'rb') as f:
                for chunk in iter(lambda: f.read(1024*1024), b''):
                    h.update(chunk)
            return h.hexdigest()

        def main():
            ap = argparse.ArgumentParser()
            ap.add_argument('--in', dest='inp', required=True)
            ap.add_argument('--out', dest='out', required=True)
            ap.add_argument('--kms', required=False)
            args = ap.parse_args()
            inp = pathlib.Path(args.inp)
            out = pathlib.Path(args.out)
            out.mkdir(parents=True, exist_ok=True)
            for p in inp.rglob('*'):
                if p.is_file():
                    sig = sha256_file(p)
                    (out/(p.name+'.sig')).write_text(f'sha256:{sig}
', encoding='utf-8')
            print('signed')

        if __name__ == '__main__':
            main()
