#!/usr/bin/env python3
import argparse, json, time, pathlib
from provenance_common import sha256_b64, write_receipt

parser = argparse.ArgumentParser()
parser.add_argument('--artifact-id', type=str, required=True)
parser.add_argument('--contributors-json', type=str, required=True)
parser.add_argument('--out', type=str, required=True)
args = parser.parse_args()
rtype = 'provenance.contribution.share.receipt'
now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
obj = {'type': rtype, 'timestamp': now}
obj.update({'artifactId': args.artifact_id, 'contributors': json.loads(args.contributors_json)})
write_receipt(args.out, obj)
