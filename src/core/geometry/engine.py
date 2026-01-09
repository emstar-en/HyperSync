
from typing import Dict, List, Optional
from ..registry import registry, ComponentManifest
from .primitives import Point
from .math_utils import poincare_distance

class GeometryEngine:
    def __init__(self):
        self.manifest = ComponentManifest(
            id="core_geometry_engine",
            version="1.0.0",
            capabilities=["geometry_calculations", "spatial_indexing"],
            priority=100
        )
        self.entities: Dict[str, Point] = {}
        self._register()

    def _register(self):
        registry.register(self.manifest.id, self, self.manifest)

    def register_entity(self, entity_id: str, x: float, y: float):
        if x**2 + y**2 >= 1:
            raise ValueError("Point must be within the unit disk (x^2 + y^2 < 1)")
        self.entities[entity_id] = Point(x, y)

    def get_distance(self, id1: str, id2: str) -> float:
        p1 = self.entities.get(id1)
        p2 = self.entities.get(id2)
        if not p1 or not p2:
            raise ValueError("Entity not found")
        return poincare_distance(p1, p2)

    def find_nearest(self, target_id: str, n: int = 1) -> List[str]:
        target = self.entities.get(target_id)
        if not target:
            return []

        distances = []
        for eid, point in self.entities.items():
            if eid == target_id:
                continue
            dist = poincare_distance(target, point)
            distances.append((eid, dist))

        distances.sort(key=lambda x: x[1])
        return [d[0] for d in distances[:n]]

# Auto-initialize
default_geometry = GeometryEngine()
