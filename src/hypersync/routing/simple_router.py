from __future__ import annotations
from pathlib import Path
import json
from typing import Dict, Optional, List

class OperatorRegistry:
    def __init__(self, operators_dir: Path):
        self.operators_dir = operators_dir
        self._ops: Dict[str, Path] = {}
        self._load()

    def _load(self):
        if not self.operators_dir.exists():
            return
        for p in self.operators_dir.glob("op_*.json"):
            try:
                data = json.loads(p.read_text())
                op_id = data.get("id") or p.stem
                if op_id:
                    self._ops[op_id] = p
            except Exception:
                continue

    def has(self, op: str) -> bool:
        return op in self._ops

    def get(self, op: str) -> Optional[Path]:
        return self._ops.get(op)

    def list(self) -> List[str]:
        return sorted(self._ops.keys())

SUPPORTED_DIRECT_OPS = {
    "op://sinkhorn_entropic.0",
    "op://sinkhorn_greenkhorn.0",
    "op://sinkhorn_unbalanced.0",
    "op://pdhg.0",
    "op://pdhg_tv_denoise.0",
    "op://geodesic_fast_marching.0",
}

class SimpleRouter:
    def __init__(self, registry: OperatorRegistry):
        self.registry = registry

    def resolve(self, op_hint: Optional[str]) -> Optional[str]:
        if op_hint and self.registry.has(op_hint):
            return op_hint
        # Allow direct known operators even if not in registry
        if op_hint in SUPPORTED_DIRECT_OPS:
            return op_hint
        # Future: infer via planner/routing rules
        raise ValueError(f"Operator not found: {op_hint}")
