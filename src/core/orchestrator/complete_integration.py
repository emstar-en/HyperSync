"""
Orchestrator Complete Wiring - Connects all orchestrator components.
"""
from hypersync.geometry.engine import get_geometry_engine
from hypersync.tokens.tracker import get_token_tracker
from hypersync.telemetry.pipeline_integration import get_telemetry_pipeline

class OrchestratorIntegration:
    """Complete orchestrator wiring."""

    def __init__(self):
        self.geometry = get_geometry_engine()
        self.token_tracker = get_token_tracker()
        self.telemetry = get_telemetry_pipeline()
        self._placement_engine = None
        self._routing_engine = None
        self._replication_engine = None

    def wire_components(self):
        """Wire all orchestrator components together."""
        # Wire placement engine with geometry
        if self._placement_engine:
            self._placement_engine.set_geometry_engine(self.geometry)

        # Wire routing with geometry and tokens
        if self._routing_engine:
            self._routing_engine.set_geometry_engine(self.geometry)
            self._routing_engine.set_token_tracker(self.token_tracker)

        # Wire replication with telemetry
        if self._replication_engine:
            self._replication_engine.set_telemetry(self.telemetry)

    def deploy(self, deployment_spec):
        """Deploy with full orchestration."""
        # Use placement engine
        placement = self._placement_engine.find_placement(deployment_spec)

        # Compute routes
        routes = self._routing_engine.compute_routes(placement)

        # Setup replication
        replication = self._replication_engine.setup_replication(placement)

        return {
            "placement": placement,
            "routes": routes,
            "replication": replication
        }
