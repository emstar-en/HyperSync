from __future__ import annotations
from pathlib import Path
import json
from typing import Any, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Very lightweight planner that tries routing rules if present,
# otherwise falls back to builtin mappings.

BUILTIN_TASK_MAP = {
    # generic tasks -> concrete operators
    'task://optimal_transport': 'op://sinkhorn_entropic.0',
    'task://optimal_transport/greenkhorn': 'op://sinkhorn_greenkhorn.0',
    'task://optimal_transport/unbalanced': 'op://sinkhorn_unbalanced.0',
    'task://optimization/pdhg': 'op://pdhg.0',
    'task://vision/tv_denoise': 'op://pdhg_tv_denoise.0',
    'task://geodesic/fast_marching': 'op://geodesic_fast_marching.0',
}

class RulesPlanner:
    def __init__(self, spec_root: Path):
        self.spec_root = spec_root
        self.plugins = {}
        self.rules = {}
        self._load()

    def _load(self):
        p_plugins = self.spec_root / 'planner' / 'registry' / 'plugins.json'
        p_rules = self.spec_root / 'planner' / 'routing' / 'geometric_unified.rules.json'
        try:
            if p_plugins.exists():
                self.plugins = json.loads(p_plugins.read_text())
        except Exception as e:
            logger.warning(f"Failed to load plugins: {e}")
            self.plugins = {}
        try:
            if p_rules.exists():
                self.rules = json.loads(p_rules.read_text())
        except Exception as e:
            logger.warning(f"Failed to load rules: {e}")
            self.rules = {}

    def plan(self, intent: Dict[str, Any]) -> Tuple[Optional[str], str]:
        # Use explicit mapping if intent.op is a routing key
        op_hint = intent.get('op')
        if op_hint in BUILTIN_TASK_MAP:
            return BUILTIN_TASK_MAP[op_hint], 'builtin task map'

        # Look for category or task markers in intent.meta/context
        meta = intent.get('meta') or {}
        ctx = intent.get('context') or {}
        for key in ('task', 'category', 'route'):
            val = (meta.get(key) or ctx.get(key))
            if isinstance(val, str) and val in BUILTIN_TASK_MAP:
                return BUILTIN_TASK_MAP[val], f'builtin via {key}'

        # Try simple rule application from rules JSON if a direct string mapping exists
        # Expected shape (loosely): { "tasks": { "task://...": "op://..." } }
        tasks = {}
        if isinstance(self.rules, dict):
            tasks = self.rules.get('tasks') or {}
        if isinstance(tasks, dict):
            if op_hint in tasks:
                return tasks[op_hint], 'rules.tasks map'
            for key in ('task', 'category', 'route'):
                val = (meta.get(key) or ctx.get(key))
                if isinstance(val, str) and val in tasks:
                    return tasks[val], f'rules via {key}'

        return None, 'no plan'


        # Advanced rules: routes list with match conditions
        # Rule format:
        # {"match": {"task": "task://...", "op": "op://...", "params": {"epsilon": {"<=": 0.05}}},
        #  "operator": "op://sinkhorn_greenkhorn.0", "set": {"params": {"accelerated": true}}}
        self.last_set = {}
        routes = {}
        if isinstance(self.rules, dict):
            routes = self.rules.get('routes') or []
        def _cmp(val, cond):
            try:
                if isinstance(cond, dict):
                    for k,v in cond.items():
                        if k == '==' and not (val == v):
                            return False
                        if k == '!=' and not (val != v):
                            return False
                        if k == '<' and not (val < v):
                            return False
                        if k == '<=' and not (val <= v):
                            return False
                        if k == '>' and not (val > v):
                            return False
                        if k == '>=' and not (val >= v):
                            return False
                        if k == 'in' and not (val in v):
                            return False
                        if k == 'not_in' and not (val not in v):
                            return False
                    return True
                else:
                    return val == cond
            except Exception:
                return False
        if isinstance(routes, list):
            params = intent.get('params') or {}
            for r in routes:
                try:
                    m = r.get('match') or {}
                    ok = True
                    if 'task' in m:
                        ok = ok and (intent.get('op') == m['task'] or (intent.get('meta') or {}).get('task') == m['task'])
                    if 'op' in m:
                        ok = ok and (intent.get('op') == m['op'])
                    mp = m.get('params') or {}
                    for k,cond in mp.items():
                        if k not in params:
                            ok = False; break
                        if not _cmp(params.get(k), cond):
                            ok = False; break
                    if not ok:
                        continue
                    # match! capture set if any
                    self.last_set = r.get('set') or {}
                    return r.get('operator'), 'rules.routes'
                except Exception as e:
                    logger.warning(f"Error processing rule {r}: {e}")
                    continue
    