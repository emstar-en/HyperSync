
from typing import List, Dict
from ..geometry.engine import default_geometry

class SpatialQuorum:
    def __init__(self, initiator_id: str, radius: float):
        self.initiator_id = initiator_id
        self.radius = radius
        self.members: List[str] = []

    def form(self) -> List[str]:
        """
        Forms a quorum based on spatial proximity in the Geometry Engine.
        """
        # In a real implementation, we would query the geometry engine for all points within radius.
        # For now, we use the nearest neighbor approximation.
        nearest = default_geometry.find_nearest(self.initiator_id, n=5)

        # Filter by actual distance (since find_nearest just sorts)
        valid_members = []
        for member_id in nearest:
            dist = default_geometry.get_distance(self.initiator_id, member_id)
            if dist <= self.radius:
                valid_members.append(member_id)

        self.members = valid_members
        return self.members
