"""
Agent System Complete Wiring - Connects all agent subsystems.
"""
from hypersync.agents.control_manager import get_control_manager
from hypersync.tokens.tracker import get_token_tracker

class AgentSystemIntegration:
    """Complete agent system wiring."""

    def __init__(self):
        self.control_manager = get_control_manager()
        self.token_tracker = get_token_tracker()
        self._composition_engine = None
        self._communication_layer = None

    def wire_agent_subsystems(self):
        """Wire all agent subsystems."""
        # Wire composition with control
        if self._composition_engine:
            self._composition_engine.set_control_manager(self.control_manager)

        # Wire communication with tokens
        if self._communication_layer:
            self._communication_layer.set_token_tracker(self.token_tracker)

    def create_agent(self, blueprint):
        """Create agent with full integration."""
        # Compose agent
        agent = self._composition_engine.compose(blueprint)

        # Register with control manager
        self.control_manager.register_agent(agent.id)

        # Setup communication
        self._communication_layer.register_agent(agent)

        return agent
