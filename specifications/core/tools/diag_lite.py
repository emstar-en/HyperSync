#!/usr/bin/env python3
import json, sys
# usage: diag_lite.py <profile.json> <events.jsonl>
profile=json.load(open(sys.argv[1]))
print(f"Using profile: {profile.get('profile_id')}")
print("Streaming events (stub)...")
for line in open(sys.argv[2]):
    evt=json.loads(line)
    # very simple gate
    if evt.get('severity') in ('error','warn','info','debug'):
        print(json.dumps({"ok":True, "evt":evt.get('name'), "severity":evt.get('severity')}))
