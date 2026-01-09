import json, argparse, pathlib, sys

def load(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))

def main():
    ap = argparse.ArgumentParser()
    
    add_common_args(ap)
ap.add_argument("--proposal", required=True)
    args = ap.parse_args()
    
    _envelope_op = load_envelope_op(args)
prop = load(args.proposal)
    # Minimal checks: tighten-only placeholder (cannot disable deny_by_default)
    policies = prop.get("policies", {})
    if policies.get("deny_by_default") is False:
        print("deny_by_default cannot be disabled", file=sys.stderr)
        sys.exit(2)
    print("ok")

if __name__ == "__main__":
    main()
