#!/usr/bin/env python3
import argparse, json, time, pathlib
from provenance_common import sha256_b64, write_receipt

parser = argparse.ArgumentParser()
parser.add_argument('--process-id', type=str, required=True)
parser.add_argument('--engine', type=str, required=True)
parser.add_argument('--params-json', type=str, required=True)
parser.add_argument('--artifact', type=str, required=False, help='path to artifact to hash')
parser.add_argument('--out', type=str, required=True)
args = parser.parse_args()
rtype = 'provenance.deterministic.process.receipt'
now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
obj = {'type': rtype, 'timestamp': now}
obj.update({'processId': args.process_id, 'engine': args.engine, 'params': json.loads(args.params_json)})
if args.artifact: obj['digest'] = sha256_b64(open(args.artifact,'rb').read())
write_receipt(args.out, obj)
