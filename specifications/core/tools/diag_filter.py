#!/usr/bin/env python3
import json, sys
# usage: diag_filter.py <rules.json> <events.jsonl>
rules=json.load(open(sys.argv[1]))
print(f"Loaded rules: {rules.get('ruleset_id')}")
for line in open(sys.argv[2]):
    evt=json.loads(line)
    # stub evaluation: print event names
    print(json.dumps({"event":evt.get('name')}))
