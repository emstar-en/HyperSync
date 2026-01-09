from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)

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
        # Lower is better. Subtract small deltas for each preference met.
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
