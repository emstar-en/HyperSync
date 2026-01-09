#!/usr/bin/env python3
import argparse, json, time, pathlib
from provenance_common import sha256_b64, write_receipt

parser = argparse.ArgumentParser()
parser.add_argument('--trace-id', type=str, required=True)
parser.add_argument('--steps-json', type=str, required=True)
parser.add_argument('--out', type=str, required=True)
args = parser.parse_args()
rtype = 'provenance.orchestration.trace.receipt'
now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
obj = {'type': rtype, 'timestamp': now}
obj.update({'traceId': args.trace_id, 'steps': json.loads(args.steps_json)})
write_receipt(args.out, obj)
