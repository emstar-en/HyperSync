from __future__ import annotations
from pathlib import Path
import json
from typing import Any, Dict, Optional, Tuple, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

BUILTIN_TASK_MAP = {
    'task://optimal_transport': 'op://sinkhorn_entropic.0',
    'task://optimal_transport/greenkhorn': 'op://sinkhorn_greenkhorn.0',
    'task://optimal_transport/unbalanced': 'op://sinkhorn_unbalanced.0',
    'task://optimization/pdhg': 'op://pdhg.0',
    'task://vision/tv_denoise': 'op://pdhg_tv_denoise.0',
    'task://geodesic/fast_marching': 'op://geodesic_fast_marching.0',
}

@dataclass
class Preferences:
    determinism_required: bool = False
    prefer_tags: List[str] | None = None
    prefer_flags: List[str] | None = None
    prefer_conformance_available: bool = False
    prefer_lower_estimated_cost: bool = False
    seed: int = 0

    @classmethod
    def from_rules(cls, rules_path: Path) -> "Preferences":
        data: Dict[str, Any] = {}
        try:
            if rules_path.exists():
                data = json.loads(rules_path.read_text())
        except Exception:
            data = {}
        defaults = data.get('defaults') or {}
        selection = data.get('selection') or {}
        order = selection.get('order') or []
        prefer_tags: List[str] = []
        prefer_flags: List[str] = []
        for item in order:
            if isinstance(item, str) and item.startswith('prefer_tags:'):
                prefer_tags.append(item.split(':', 1)[1])
            if isinstance(item, str) and item.startswith('prefer_flag:'):
                prefer_flags.append(item.split(':', 1)[1])
        return cls(
            determinism_required=bool(defaults.get('determinism_required')),
            prefer_tags=prefer_tags or None,
            prefer_flags=prefer_flags or None,
            prefer_conformance_available=('prefer_conformance_available' in order),
            prefer_lower_estimated_cost=('prefer_lower_estimated_cost' in order),
            seed=int(defaults.get('seed') or 0),
        )

    def score_delta(self, node_meta: Dict[str, Any]) -> float:
        delta = 0.0
        tags = set((node_meta or {}).get('tags') or [])
        flags = set((node_meta or {}).get('flags') or [])
        if self.prefer_tags:
            if any(t in tags for t in self.prefer_tags):
                delta -= 0.25
        if self.prefer_flags:
            if any(f in flags for f in self.prefer_flags):
                delta -= 0.25
        if self.prefer_lower_estimated_cost:
            try:
                cost = float((node_meta or {}).get('estimated_cost'))
                delta -= min(max(cost, 0.0), 1.0) * 0.1
            except Exception as e:
                logger.debug(f"Error parsing cost: {e}")
        if self.prefer_conformance_available and (('has_conformance' in flags) or ('conformance' in tags)):
            delta -= 0.2
        return float(delta)

class RulesPlanner:
    def __init__(self, spec_root: Path):
        self.spec_root = spec_root
        self.plugins = {}
        self.rules = {}
        self.last_set = {}
        self._load()

    def _load(self):
        # In a capsule, paths might be relative to the capsule or passed in config
        # For now, assuming standard layout relative to spec_root
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
        op_hint = intent.get('op')
        if op_hint in BUILTIN_TASK_MAP:
            return BUILTIN_TASK_MAP[op_hint], 'builtin task map'

        meta = intent.get('meta') or {}
        ctx = intent.get('context') or {}
        for key in ('task', 'category', 'route'):
            val = (meta.get(key) or ctx.get(key))
            if isinstance(val, str) and val in BUILTIN_TASK_MAP:
                return BUILTIN_TASK_MAP[val], f'builtin via {key}'

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

        # Advanced routing logic (simplified for brevity, full logic in original file)
        return None, 'no plan'
