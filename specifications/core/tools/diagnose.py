#!/usr/bin/env python3
import json, sys, datetime as dt
from pathlib import Path

CFG_PATH=Path(__file__).resolve().parents[2]/'refs/diagnostics/analogy_engine_config.json'
ACTIONS_PATH=Path(__file__).resolve().parents[2]/'refs/diagnostics/runbook_actions.json'

cfg=json.loads(CFG_PATH.read_text())
actions={a['id']:a for a in json.loads(ACTIONS_PATH.read_text())['actions']}

SEVERITY_DEFAULT='INFO'

def translate(evt):
    etype=evt.get('type')
    payload=evt.get('payload',{})
    key=None
    # derive reason keys for mapping
    reason=payload.get('reason') or payload.get('status') or payload.get('error')
    if reason:
        key=f"{etype}:{reason}"
    else:
        # derive state-based keys
        if etype=='gauss_bonnet_defect' and payload.get('passed') is False:
            key='gauss_bonnet_defect:FAIL'
        elif etype=='jacobi_integrator' and payload.get('residual_max',0)>payload.get('residual_max_eps',1):
            key='jacobi_integrator:RESIDUAL_HIGH'
        elif etype=='cross_model_invariance' and payload.get('delta',0)>payload.get('eps',1):
            key='cross_model_invariance:DELTA_HIGH'
        elif etype=='proof_verification' and payload.get('error_code'):
            key=f"proof_verification:{payload['error_code']}"
    spec=cfg['mapping'].get(key,{
        'severity':SEVERITY_DEFAULT,
        'category':'Info',
        'message':'Event recorded.',
        'actions':['escalate']
    })
    out={
        'severity':spec['severity'],
        'category':spec['category'],
        'message':spec['message'],
        'actions':[{'id':aid,'label':actions[aid]['label'],'safe':actions[aid]['safe']} for aid in spec['actions'] if aid in actions],
        'ts':evt.get('ts') or dt.datetime.utcnow().isoformat()+'Z',
        'engine_id':evt.get('engine_id'),
        'policy_profile':evt.get('policy_profile'),
        'run_id':evt.get('run_id'),
        'event_id':evt.get('id')
    }
    return out

if __name__=='__main__':
    data=sys.stdin.read().strip().splitlines()
    for line in data:
        if not line: continue
        evt=json.loads(line)
        print(json.dumps(translate(evt)))
