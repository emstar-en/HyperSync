#!/usr/bin/env python3
"""Ops router stub: consume EnvelopeRouteOp and emit normalized op."""
import argparse, json, sys
ap = argparse.ArgumentParser()
ap.add_argument("--op-json")
args = ap.parse_args()
op = {}
if args.op_json:
    try:
        with open(args.op_json, "r", encoding="utf-8") as fh:
            op = json.load(fh)
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)})); sys.exit(1)
print(json.dumps({"ok": True, "op": op}))
