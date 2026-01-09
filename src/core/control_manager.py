"""
Agent Control Manager - Central manager for agent runtime control.

Coordinates agent lifecycle, resource enforcement, and runtime monitoring.
"""
import logging
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent lifecycle states."""
    INITIALIZING = "initializing"
    STARTING = "starting"
    RUNNING = "running"
    PAUSING = "pausing"
    PAUSED = "paused"
    RESUMING = "resuming"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    TERMINATED = "terminated"


@dataclass
class AgentControlConfig:
    """Configuration for agent control."""
    agent_id: str
    max_memory_mb: int = 1024
    max_cpu_percent: float = 80.0
    max_runtime_seconds: Optional[int] = None
    enable_resource_limits: bool = True
    enable_lifecycle_hooks: bool = True
    enable_telemetry: bool = True
    restart_on_failure: bool = False
    max_restart_attempts: int = 3


@dataclass
class AgentRuntimeInfo:
    """Runtime information for an agent."""
    agent_id: str
    state: AgentState
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    restart_count: int = 0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentControlManager:
    """
    Central manager for agent runtime control.

    Responsibilities:
    - Manage agent lifecycle states
    - Coordinate control modules
    - Enforce resource limits
    - Execute lifecycle hooks
    - Monitor agent runtime
    """

    def __init__(self):
        self._agents: Dict[str, AgentRuntimeInfo] = {}
        self._configs: Dict[str, AgentControlConfig] = {}
        self._lifecycle_coordinator = None
        self._resource_enforcer = None
        self._hooks_registry = None

    def set_lifecycle_coordinator(self, coordinator):
        """Set the lifecycle coordinator."""
        self._lifecycle_coordinator = coordinator
        logger.info("Lifecycle coordinator registered")

    def set_resource_enforcer(self, enforcer):
        """Set the resource enforcer."""
        self._resource_enforcer = enforcer
        logger.info("Resource enforcer registered")

    def set_hooks_registry(self, registry):
        """Set the hooks registry."""
        self._hooks_registry = registry
        logger.info("Hooks registry registered")

    def register_agent(
        self,
        agent_id: str,
        config: Optional[AgentControlConfig] = None
    ) -> None:
        """
        Register an agent with the control manager.

        Args:
            agent_id: Agent identifier
            config: Control configuration (uses defaults if None)
        """
        if agent_id in self._agents:
            logger.warning(f"Agent {agent_id} already registered, updating")

        # Use provided config or create default
        if config is None:
            config = AgentControlConfig(agent_id=agent_id)

        self._configs[agent_id] = config

        # Create runtime info
        runtime_info = AgentRuntimeInfo(
            agent_id=agent_id,
            state=AgentState.INITIALIZING
        )

        self._agents[agent_id] = runtime_info

        logger.info(f"Registered agent: {agent_id}")

    def start_agent(self, agent_id: str) -> bool:
        """
        Start an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            True if started successfully
        """
        if agent_id not in self._agents:
            logger.error(f"Agent {agent_id} not registered")
            return False

        runtime_info = self._agents[agent_id]
        config = self._configs[agent_id]

        try:
            # Execute pre-start hooks
            if config.enable_lifecycle_hooks and self._hooks_registry:
                self._hooks_registry.execute_hooks("pre_start", agent_id)

            # Transition to starting state
            runtime_info.state = AgentState.STARTING
            runtime_info.started_at = datetime.now()

            # Use lifecycle coordinator if available
            if self._lifecycle_coordinator:
                self._lifecycle_coordinator.handle_start(agent_id)

            # Transition to running state
            runtime_info.state = AgentState.RUNNING

            # Execute post-start hooks
            if config.enable_lifecycle_hooks and self._hooks_registry:
                self._hooks_registry.execute_hooks("post_start", agent_id)

            logger.info(f"Started agent: {agent_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to start agent {agent_id}: {e}", exc_info=True)
            runtime_info.state = AgentState.ERROR
            runtime_info.error_message = str(e)
            return False

    def stop_agent(self, agent_id: str) -> bool:
        """
        Stop an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            True if stopped successfully
        """
        if agent_id not in self._agents:
            logger.error(f"Agent {agent_id} not registered")
            return False

        runtime_info = self._agents[agent_id]
        config = self._configs[agent_id]

        try:
            # Execute pre-stop hooks
            if config.enable_lifecycle_hooks and self._hooks_registry:
                self._hooks_registry.execute_hooks("pre_stop", agent_id)

            # Transition to stopping state
            runtime_info.state = AgentState.STOPPING

            # Use lifecycle coordinator if available
            if self._lifecycle_coordinator:
                self._lifecycle_coordinator.handle_stop(agent_id)

            # Transition to stopped state
            runtime_info.state = AgentState.STOPPED
            runtime_info.stopped_at = datetime.now()

            # Execute post-stop hooks
            if config.enable_lifecycle_hooks and self._hooks_registry:
                self._hooks_registry.execute_hooks("post_stop", agent_id)

            logger.info(f"Stopped agent: {agent_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to stop agent {agent_id}: {e}", exc_info=True)
            runtime_info.state = AgentState.ERROR
            runtime_info.error_message = str(e)
            return False

    def pause_agent(self, agent_id: str) -> bool:
        """Pause an agent."""
        if agent_id not in self._agents:
            return False

        runtime_info = self._agents[agent_id]

        if runtime_info.state != AgentState.RUNNING:
            logger.warning(f"Agent {agent_id} not running, cannot pause")
            return False

        runtime_info.state = AgentState.PAUSING

        if self._lifecycle_coordinator:
            self._lifecycle_coordinator.handle_pause(agent_id)

        runtime_info.state = AgentState.PAUSED
        logger.info(f"Paused agent: {agent_id}")
        return True

    def resume_agent(self, agent_id: str) -> bool:
        """Resume a paused agent."""
        if agent_id not in self._agents:
            return False

        runtime_info = self._agents[agent_id]

        if runtime_info.state != AgentState.PAUSED:
            logger.warning(f"Agent {agent_id} not paused, cannot resume")
            return False

        runtime_info.state = AgentState.RESUMING

        if self._lifecycle_coordinator:
            self._lifecycle_coordinator.handle_resume(agent_id)

        runtime_info.state = AgentState.RUNNING
        logger.info(f"Resumed agent: {agent_id}")
        return True

    def update_runtime_metrics(
        self,
        agent_id: str,
        memory_mb: float,
        cpu_percent: float
    ) -> None:
        """
        Update runtime metrics for an agent.

        Args:
            agent_id: Agent identifier
            memory_mb: Memory usage in MB
            cpu_percent: CPU usage percentage
        """
        if agent_id not in self._agents:
            return

        runtime_info = self._agents[agent_id]
        runtime_info.memory_usage_mb = memory_mb
        runtime_info.cpu_usage_percent = cpu_percent

        # Check resource limits
        if self._resource_enforcer:
            config = self._configs[agent_id]
            if config.enable_resource_limits:
                self._resource_enforcer.check_limits(agent_id, runtime_info, config)

    def get_agent_state(self, agent_id: str) -> Optional[AgentState]:
        """Get current state of an agent."""
        if agent_id not in self._agents:
            return None
        return self._agents[agent_id].state

    def get_runtime_info(self, agent_id: str) -> Optional[AgentRuntimeInfo]:
        """Get runtime information for an agent."""
        return self._agents.get(agent_id)

    def list_agents(
        self,
        state: Optional[AgentState] = None
    ) -> List[AgentRuntimeInfo]:
        """
        List agents, optionally filtered by state.

        Args:
            state: Filter by state (None = all)

        Returns:
            List of agent runtime info
        """
        agents = list(self._agents.values())

        if state:
            agents = [a for a in agents if a.state == state]

        return agents

    def get_status(self) -> Dict[str, Any]:
        """Get control manager status."""
        state_counts = {}
        for state in AgentState:
            count = len([a for a in self._agents.values() if a.state == state])
            if count > 0:
                state_counts[state.value] = count

        return {
            "total_agents": len(self._agents),
            "state_counts": state_counts,
            "lifecycle_coordinator_enabled": self._lifecycle_coordinator is not None,
            "resource_enforcer_enabled": self._resource_enforcer is not None,
            "hooks_registry_enabled": self._hooks_registry is not None
        }


# Global control manager instance
_control_manager: Optional[AgentControlManager] = None


def get_control_manager() -> AgentControlManager:
    """Get the global agent control manager instance."""
    global _control_manager
    if _control_manager is None:
        _control_manager = AgentControlManager()
    return _control_manager
