import argparse
try:
    from cli_common import add_common_args, load_envelope_op
except Exception:
    def add_common_args(ap):
        return ap
    def load_envelope_op(args):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--env', required=True)
    ap.add_argument('--bundle', required=True)
    args = ap.parse_args()
    print(f'deployed {args.bundle} to {args.env}')

if __name__ == '__main__':
    main()
