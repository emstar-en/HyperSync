"""
Resource Enforcer - Enforces resource limits on agents.

Monitors and enforces memory, CPU, and runtime limits.
"""
import logging
from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class ResourceViolation:
    """Represents a resource limit violation."""
    agent_id: str
    violation_type: str  # "memory", "cpu", "runtime"
    limit: float
    actual: float
    timestamp: datetime
    action_taken: str  # "warning", "throttle", "terminate"


class ResourceEnforcer:
    """
    Enforces resource limits on agents.

    Responsibilities:
    - Monitor resource usage
    - Enforce limits (memory, CPU, runtime)
    - Take corrective actions
    - Track violations
    """

    def __init__(self):
        self._violations: Dict[str, list] = {}
        self._warning_callbacks: list = []
        self._throttle_callbacks: list = []
        self._terminate_callbacks: list = []

    def register_warning_callback(self, callback: Callable):
        """Register callback for warning actions."""
        self._warning_callbacks.append(callback)

    def register_throttle_callback(self, callback: Callable):
        """Register callback for throttle actions."""
        self._throttle_callbacks.append(callback)

    def register_terminate_callback(self, callback: Callable):
        """Register callback for terminate actions."""
        self._terminate_callbacks.append(callback)

    def check_limits(self, agent_id: str, runtime_info, config) -> None:
        """
        Check resource limits for an agent.

        Args:
            agent_id: Agent identifier
            runtime_info: Current runtime information
            config: Agent control configuration
        """
        # Check memory limit
        if runtime_info.memory_usage_mb > config.max_memory_mb:
            self._handle_memory_violation(
                agent_id=agent_id,
                limit=config.max_memory_mb,
                actual=runtime_info.memory_usage_mb
            )

        # Check CPU limit
        if runtime_info.cpu_usage_percent > config.max_cpu_percent:
            self._handle_cpu_violation(
                agent_id=agent_id,
                limit=config.max_cpu_percent,
                actual=runtime_info.cpu_usage_percent
            )

        # Check runtime limit
        if config.max_runtime_seconds and runtime_info.started_at:
            elapsed = (datetime.now() - runtime_info.started_at).total_seconds()
            if elapsed > config.max_runtime_seconds:
                self._handle_runtime_violation(
                    agent_id=agent_id,
                    limit=config.max_runtime_seconds,
                    actual=elapsed
                )

    def _handle_memory_violation(
        self,
        agent_id: str,
        limit: float,
        actual: float
    ) -> None:
        """Handle memory limit violation."""
        logger.warning(
            f"Memory violation for agent {agent_id}: "
            f"{actual:.1f}MB > {limit:.1f}MB"
        )

        # Determine severity
        overage_percent = ((actual - limit) / limit) * 100

        if overage_percent < 10:
            # Minor overage - warning
            action = "warning"
            self._execute_callbacks(self._warning_callbacks, agent_id, "memory")
        elif overage_percent < 50:
            # Moderate overage - throttle
            action = "throttle"
            self._execute_callbacks(self._throttle_callbacks, agent_id, "memory")
        else:
            # Severe overage - terminate
            action = "terminate"
            self._execute_callbacks(self._terminate_callbacks, agent_id, "memory")

        # Record violation
        self._record_violation(
            agent_id=agent_id,
            violation_type="memory",
            limit=limit,
            actual=actual,
            action_taken=action
        )

    def _handle_cpu_violation(
        self,
        agent_id: str,
        limit: float,
        actual: float
    ) -> None:
        """Handle CPU limit violation."""
        logger.warning(
            f"CPU violation for agent {agent_id}: "
            f"{actual:.1f}% > {limit:.1f}%"
        )

        # CPU violations typically result in throttling
        action = "throttle"
        self._execute_callbacks(self._throttle_callbacks, agent_id, "cpu")

        self._record_violation(
            agent_id=agent_id,
            violation_type="cpu",
            limit=limit,
            actual=actual,
            action_taken=action
        )

    def _handle_runtime_violation(
        self,
        agent_id: str,
        limit: float,
        actual: float
    ) -> None:
        """Handle runtime limit violation."""
        logger.warning(
            f"Runtime violation for agent {agent_id}: "
            f"{actual:.1f}s > {limit:.1f}s"
        )

        # Runtime violations result in termination
        action = "terminate"
        self._execute_callbacks(self._terminate_callbacks, agent_id, "runtime")

        self._record_violation(
            agent_id=agent_id,
            violation_type="runtime",
            limit=limit,
            actual=actual,
            action_taken=action
        )

    def _execute_callbacks(
        self,
        callbacks: list,
        agent_id: str,
        violation_type: str
    ) -> None:
        """Execute registered callbacks."""
        for callback in callbacks:
            try:
                callback(agent_id, violation_type)
            except Exception as e:
                logger.error(f"Callback execution failed: {e}", exc_info=True)

    def _record_violation(
        self,
        agent_id: str,
        violation_type: str,
        limit: float,
        actual: float,
        action_taken: str
    ) -> None:
        """Record a resource violation."""
        violation = ResourceViolation(
            agent_id=agent_id,
            violation_type=violation_type,
            limit=limit,
            actual=actual,
            timestamp=datetime.now(),
            action_taken=action_taken
        )

        if agent_id not in self._violations:
            self._violations[agent_id] = []

        self._violations[agent_id].append(violation)
        logger.debug(f"Recorded violation: {agent_id} {violation_type} -> {action_taken}")

    def get_violations(
        self,
        agent_id: Optional[str] = None
    ) -> Dict[str, list]:
        """
        Get violation history.

        Args:
            agent_id: Specific agent (None = all)

        Returns:
            Dictionary of violations by agent
        """
        if agent_id:
            return {agent_id: self._violations.get(agent_id, [])}
        return self._violations.copy()

    def clear_violations(self, agent_id: str) -> None:
        """Clear violation history for an agent."""
        if agent_id in self._violations:
            del self._violations[agent_id]
            logger.info(f"Cleared violations for agent: {agent_id}")

    def get_status(self) -> Dict[str, Any]:
        """Get enforcer status."""
        total_violations = sum(len(v) for v in self._violations.values())

        violation_counts = {}
        for violations in self._violations.values():
            for v in violations:
                violation_counts[v.violation_type] =                     violation_counts.get(v.violation_type, 0) + 1

        return {
            "total_agents_with_violations": len(self._violations),
            "total_violations": total_violations,
            "violation_counts": violation_counts,
            "warning_callbacks": len(self._warning_callbacks),
            "throttle_callbacks": len(self._throttle_callbacks),
            "terminate_callbacks": len(self._terminate_callbacks)
        }
