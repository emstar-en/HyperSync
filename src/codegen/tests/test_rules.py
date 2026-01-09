import json
from pathlib import Path
from hypersync.planner.rules import RulesPlanner

def test_rules_routes(tmp_path):
    spec_root = tmp_path / 'spec_pack'
    (spec_root / 'planner/routing').mkdir(parents=True)
    rules = {
        "routes": [
            {"match": {"task": "task://optimal_transport/greenkhorn", "params": {"epsilon": {"<=": 0.2}}},
             "operator": "op://sinkhorn_greenkhorn.0",
             "set": {"params": {"accelerated": True, "momentum": 0.3}}}
        ]
    }
    (spec_root / 'planner/routing/geometric_unified.rules.json').write_text(json.dumps(rules))
    planner = RulesPlanner(spec_root)
    intent = {"op": "task://optimal_transport/greenkhorn", "params": {"epsilon": 0.1}}
    op, why = planner.plan(intent)
    assert op == 'op://sinkhorn_greenkhorn.0'
    assert planner.last_set.get('params', {}).get('accelerated') is True
