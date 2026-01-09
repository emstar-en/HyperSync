from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
from ..hypergraph.build import SpecGraphBuilderRules
from ..coord.coordinator import Coordinator, ModelAdapter, OperatorModel, FunctionModel
from ..planner.prefs import Preferences
from ..policy.gate import PolicyGate
from ..hypergraph.model import ModelNode, HyperGraph

class ProgramEngine:
    def __init__(self, spec_root: Path):
        self.spec_root = spec_root

    def build_default(self) -> tuple[Coordinator, HyperGraph]:
        builder = SpecGraphBuilderRules(self.spec_root)
        g = builder.build()
        # register adapters for each node (operator-backed)
        adapters = {}
        for nid, node in g.nodes.items():
            adapters[nid] = OperatorModel(node, self.spec_root)
        # choose arbitrary start as the lexicographically smallest id
        rp = self.spec_root / "planner" / "routing" / "geometric_unified.rules.json"
        prefs = Preferences.from_rules(rp) if rp.exists() else None
        # Load defaults for policy
        defaults = {}
        try:
            import json
            defaults = json.loads(rp.read_text()).get('defaults', {}) if rp.exists() else {}
        except Exception:
            defaults = {}
        gate = PolicyGate()
        gate.policy = {
            "deterministic": bool(defaults.get("determinism_required")),
            "tier_gating": (defaults.get("tier_gating") or "off"),
            "privacy_enforced": bool(defaults.get("privacy_enforced")),
            # Tier can be overridden at runtime via env HYPERSYNC_TIER; default Core
            "tier": __import__("os").environ.get("HYPERSYNC_TIER", "Core")
        }
        coord = Coordinator(self.spec_root, g, adapters, prefs=prefs, gate=gate)
        return coord, g

    def run(self, task: str, payload: Dict[str, Any], max_steps: int = 4) -> Dict[str, Any]:
        coord, g = self.build_default()
        start = sorted(g.nodes.keys())[0]
        return coord.run_program(start=start, task=task, payload=payload, max_steps=max_steps)
