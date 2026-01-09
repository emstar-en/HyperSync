#!/usr/bin/env python3
import argparse, json, time, pathlib
from provenance_common import sha256_b64, write_receipt

parser = argparse.ArgumentParser()
parser.add_argument('--model-id', type=str, required=True)
parser.add_argument('--version', type=str, required=True)
parser.add_argument('--parents', type=str, required=True)
parser.add_argument('--out', type=str, required=True)
args = parser.parse_args()
rtype = 'provenance.model.lineage.receipt'
now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
obj = {'type': rtype, 'timestamp': now}
obj.update({'modelId': args.model_id, 'version': args.version, 'lineage': json.loads(args.parents)})
write_receipt(args.out, obj)
