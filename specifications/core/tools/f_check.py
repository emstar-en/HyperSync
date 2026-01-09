#!/usr/bin/env python3
"""System F portability tool stub."""
import argparse, json, sys
try:
    from cli_common import add_common_args, load_envelope_op
except Exception:
    def add_common_args(ap):
        return ap
    def load_envelope_op(args):
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--erasure", action="store_true")
    ap.add_argument("--input", "-i", type=str, help="Input JSON")
    args = ap.parse_args()
    payload = {"ok": True, "erasure": args.erasure, "tool": "f_check.py"}
    print(json.dumps(payload))
if __name__ == "__main__":
    main()
