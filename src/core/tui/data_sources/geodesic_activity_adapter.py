"""Geodesic activity adapter."""
import random
from . import DataAdapter

class GeodesicActivityAdapter(DataAdapter):
    """Adapter for geodesic activity curves."""

    def __init__(self):
        super().__init__("geodesic.activity")
        self.history = []

    async def fetch(self):
        """Fetch geodesic activity data."""
        # TODO: Connect to actual geodesic telemetry
        # Mock time-series data
        value = random.uniform(0.3, 0.9)
        self.history.append(value)

        if len(self.history) > 100:
            self.history.pop(0)

        return {"activity": self.history}
