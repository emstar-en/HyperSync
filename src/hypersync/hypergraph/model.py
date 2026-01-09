from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class Channel:
    name: str
    desc: str = ''
    schema: Optional[Dict[str, Any]] = None

@dataclass
class ModelNode:
    id: str
    kind: str = 'function'  # 'function' | 'operator' | 'service'
    capabilities: List[str] = field(default_factory=list)  # topics or op ids
    meta: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HyperEdge:
    # Hyperedge connects k>=2 nodes, labeled by channel/capability
    label: str
    nodes: List[str]
    weight: float = 1.0

@dataclass
class HyperGraph:
    nodes: Dict[str, ModelNode] = field(default_factory=dict)
    edges: List[HyperEdge] = field(default_factory=list)

    def add_node(self, node: ModelNode):
        self.nodes[node.id] = node

    def add_edge(self, edge: HyperEdge):
        self.edges.append(edge)

    def neighbors(self, node_id: str) -> List[str]:
        nbrs = set()
        for e in self.edges:
            if node_id in e.nodes:
                for nid in e.nodes:
                    if nid != node_id:
                        nbrs.add(nid)
        return sorted(nbrs)
