from __future__ import annotations
from typing import Dict, Any
from ..hypergraph.embed import EmbeddingStore

class HyperbolicRouter:
    def __init__(self, seed: int = 0):
        self.embed = EmbeddingStore(8, 1.0, seed)
    def route(self, options: Dict[str, Any], task: str) -> str:
        # options: id -> features; choose min distance to task tag
        scored = sorted([(self.embed.distance(task, k), k) for k in options.keys()])
        return scored[0][1]
