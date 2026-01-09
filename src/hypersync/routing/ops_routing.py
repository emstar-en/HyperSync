from __future__ import annotations
from typing import List, Dict, Any
import logging
from ..hypergraph.embed import EmbeddingStore
from ..planner.prefs import Preferences
from ..policy.gate import PolicyGate
from ..router.simple_router import OperatorRegistry

logger = logging.getLogger(__name__)

class RoutingOps:
    def __init__(self, dim: int = 8, curvature: float = -1.0, radius_cap: float = 0.98, seed: int = 0, prefs: Preferences | None = None, gate: PolicyGate | None = None, registry: OperatorRegistry | None = None):
        self.embed = EmbeddingStore(dim, curvature, radius_cap, seed)
        self.prefs = prefs
        self.gate = gate
        self.registry = registry

    def _score_node(self, n: str) -> float:
        base = 0.0
        if self.prefs and self.registry:
            try:
                import json
                meta = {}
                pp = self.registry.get(n)
                if pp:
                    meta = json.loads(pp.read_text())
                tags = set(meta.get('tags') or [])
                tags.add(n)
                meta['tags'] = sorted(tags)
                base += self.prefs.score_delta(meta)
            except Exception as e:
                logger.warning(f"Error scoring node {n}: {e}")
        return base

    def next_hop(self, current: str, neighbors: List[str], task_tag: str) -> str:
        cands = []
        for n in neighbors:
            # policy filter
            if self.gate and self.registry:
                try:
                    import json
                    pp = self.registry.get(n)
                    meta = json.loads(pp.read_text()) if pp else {}
                    ok, _ = self.gate.check_operator(meta)
                    if not ok:
                        continue
                except Exception as e:
                    logger.warning(f"Error checking operator {n}: {e}")
            d = self.embed.distance(task_tag, n) + self._score_node(n)
            cands.append((d, n))
        if not cands:
            cands = [(self.embed.distance(task_tag, n), n) for n in neighbors]
        scored = sorted(cands, key=lambda x: x[0])
        return scored[0][1]

    def route_path(self, start: str, candidates: List[str], task_tag: str, max_steps: int = 5, top_k: int = 3) -> List[str]:
        path = [start]
        cur = start
        for _ in range(max_steps):
            nbrs = [n for n in candidates if n != cur]
            if not nbrs:
                break
            # shortlist top-k by score then apply policy again
            scored = []
            for n in nbrs:
                s = self.embed.distance(task_tag, n) + self._score_node(n)
                scored.append((s, n))
            scored.sort(key=lambda x: x[0])
            shortlist = [n for _, n in scored[:max(1, top_k)]]
            chosen = None
            for n in shortlist:
                if self.gate and self.registry:
                    import json
                    pp = self.registry.get(n)
                    meta = json.loads(pp.read_text()) if pp else {}
                    ok, _ = self.gate.check_operator(meta)
                    if not ok:
                        continue
                chosen = n
                break
            if chosen is None:
                chosen = shortlist[0]
            nxt = chosen
            path.append(nxt)
            cur = nxt
        return path
