#!/usr/bin/env python3
import json, sys, datetime as dt
from pathlib import Path

BASE=Path(__file__).resolve().parents[2]
ATT=BASE/'refs/conformance/vectors/non_euclidean/attestations_expanded.jsonl'

def read_recent_attestations(limit=20):
    if not ATT.exists():
        return []
    lines=ATT.read_text().strip().splitlines()[-limit:]
    return [json.loads(l) for l in lines]

def main():
    events=[json.loads(l) for l in sys.stdin.read().strip().splitlines() if l.strip()]
    capsule={
        'id': f"caps-{dt.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
        'ts': dt.datetime.utcnow().isoformat()+'Z',
        'policy_profile': events[0].get('policy_profile') if events else 'production',
        'engine_id': events[0].get('engine_id') if events else 'unknown',
        'events': events,
        'attestations': read_recent_attestations()
    }
    print(json.dumps(capsule, indent=2))

if __name__=='__main__':
    main()
