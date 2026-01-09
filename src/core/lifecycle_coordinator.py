"""
Lifecycle Coordinator - Coordinates agent lifecycle transitions.

Manages state transitions and integrates with existing runtime control modules.
"""
import logging
from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


@dataclass
class LifecycleTransition:
    """Represents a lifecycle state transition."""
    from_state: str
    to_state: str
    agent_id: str
    timestamp: float
    metadata: Dict[str, Any]


class LifecycleCoordinator:
    """
    Coordinates agent lifecycle transitions.

    Responsibilities:
    - Handle lifecycle events (start, stop, pause, resume)
    - Integrate with runtime control modules
    - Track state transitions
    - Execute transition logic
    """

    def __init__(self):
        self._transitions: Dict[str, list] = {}
        self._runtime_control = None
        self._lifecycle_hooks = None

    def set_runtime_control(self, control):
        """Set the runtime control module."""
        self._runtime_control = control
        logger.info("Runtime control module registered")

    def set_lifecycle_hooks(self, hooks):
        """Set the lifecycle hooks module."""
        self._lifecycle_hooks = hooks
        logger.info("Lifecycle hooks module registered")

    def handle_start(self, agent_id: str) -> bool:
        """
        Handle agent start event.

        Args:
            agent_id: Agent identifier

        Returns:
            True if handled successfully
        """
        logger.info(f"Handling start for agent: {agent_id}")

        try:
            # Use runtime control if available
            if self._runtime_control:
                self._runtime_control.initialize_agent(agent_id)

            # Record transition
            self._record_transition(
                agent_id=agent_id,
                from_state="initializing",
                to_state="running"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to handle start for {agent_id}: {e}", exc_info=True)
            return False

    def handle_stop(self, agent_id: str) -> bool:
        """
        Handle agent stop event.

        Args:
            agent_id: Agent identifier

        Returns:
            True if handled successfully
        """
        logger.info(f"Handling stop for agent: {agent_id}")

        try:
            # Use runtime control if available
            if self._runtime_control:
                self._runtime_control.cleanup_agent(agent_id)

            # Record transition
            self._record_transition(
                agent_id=agent_id,
                from_state="running",
                to_state="stopped"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to handle stop for {agent_id}: {e}", exc_info=True)
            return False

    def handle_pause(self, agent_id: str) -> bool:
        """Handle agent pause event."""
        logger.info(f"Handling pause for agent: {agent_id}")

        try:
            if self._runtime_control:
                self._runtime_control.pause_agent(agent_id)

            self._record_transition(
                agent_id=agent_id,
                from_state="running",
                to_state="paused"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to handle pause for {agent_id}: {e}", exc_info=True)
            return False

    def handle_resume(self, agent_id: str) -> bool:
        """Handle agent resume event."""
        logger.info(f"Handling resume for agent: {agent_id}")

        try:
            if self._runtime_control:
                self._runtime_control.resume_agent(agent_id)

            self._record_transition(
                agent_id=agent_id,
                from_state="paused",
                to_state="running"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to handle resume for {agent_id}: {e}", exc_info=True)
            return False

    def _record_transition(
        self,
        agent_id: str,
        from_state: str,
        to_state: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a state transition."""
        import time

        transition = LifecycleTransition(
            from_state=from_state,
            to_state=to_state,
            agent_id=agent_id,
            timestamp=time.time(),
            metadata=metadata or {}
        )

        if agent_id not in self._transitions:
            self._transitions[agent_id] = []

        self._transitions[agent_id].append(transition)
        logger.debug(f"Recorded transition: {agent_id} {from_state} -> {to_state}")

    def get_transitions(self, agent_id: str) -> list:
        """Get transition history for an agent."""
        return self._transitions.get(agent_id, [])

    def get_status(self) -> Dict[str, Any]:
        """Get coordinator status."""
        return {
            "total_agents_tracked": len(self._transitions),
            "total_transitions": sum(len(t) for t in self._transitions.values()),
            "runtime_control_enabled": self._runtime_control is not None,
            "lifecycle_hooks_enabled": self._lifecycle_hooks is not None
        }
