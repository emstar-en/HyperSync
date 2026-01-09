"""
HyperSync Agent Telemetry Collector

Collects and emits structured telemetry events for agent operations.
Integrates with OpenTelemetry for distributed tracing.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Agent telemetry event types."""
    AGENT_CREATED = "agent.created"
    AGENT_ACTIVATED = "agent.activated"
    AGENT_SUSPENDED = "agent.suspended"
    AGENT_DELETED = "agent.deleted"
    AGENT_UPDATED = "agent.updated"
    DELEGATION_STARTED = "delegation.started"
    DELEGATION_COMPLETED = "delegation.completed"
    DELEGATION_FAILED = "delegation.failed"
    CLEARANCE_CHECKED = "clearance.checked"
    CLEARANCE_ESCALATED = "clearance.escalated"
    CLEARANCE_DENIED = "clearance.denied"
    REDACTION_APPLIED = "redaction.applied"
    POLICY_EVALUATED = "policy.evaluated"
    POLICY_VIOLATED = "policy.violated"
    COMPOSITION_STARTED = "composition.started"
    COMPOSITION_COMPLETED = "composition.completed"
    COMPOSITION_FAILED = "composition.failed"


class AgentTelemetryCollector:
    """
    Collects and emits agent telemetry events.

    Provides structured event emission with distributed tracing support.
    """

    def __init__(self, exporters: Optional[List[Any]] = None,
                 enable_tracing: bool = True):
        """
        Initialize telemetry collector.

        Args:
            exporters: List of telemetry exporters
            enable_tracing: Enable distributed tracing
        """
        self.exporters = exporters or []
        self.enable_tracing = enable_tracing
        self.events: List[Dict] = []

    def emit_event(self, event_type: EventType, agent_id: str,
                   requester_id: Optional[str] = None,
                   attributes: Optional[Dict] = None,
                   security_context: Optional[Dict] = None,
                   trace_id: Optional[str] = None,
                   span_id: Optional[str] = None,
                   parent_span_id: Optional[str] = None) -> str:
        """
        Emit a telemetry event.

        Args:
            event_type: Type of event
            agent_id: Agent identifier
            requester_id: Original requester identifier
            attributes: Event-specific attributes
            security_context: Security-relevant context
            trace_id: Distributed trace ID
            span_id: Span ID
            parent_span_id: Parent span ID

        Returns:
            Event ID
        """
        event_id = f"evt-{uuid.uuid4().hex[:16]}"

        event = {
            'event_id': event_id,
            'event_type': event_type.value,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'agent_id': agent_id,
            'requester_id': requester_id,
            'trace_id': trace_id or self._generate_trace_id(),
            'span_id': span_id or self._generate_span_id(),
            'parent_span_id': parent_span_id,
            'attributes': attributes or {},
            'security_context': security_context or {},
            'metadata': {}
        }

        # Store event
        self.events.append(event)

        # Export to configured exporters
        for exporter in self.exporters:
            try:
                exporter.export(event)
            except Exception as e:
                logger.error(f"Failed to export event to {exporter}: {e}")

        logger.debug(f"Emitted event: {event_type.value} for agent {agent_id}")
        return event_id

    def emit_lifecycle_event(self, event_type: EventType, agent_id: str,
                            profile: Dict, trace_id: Optional[str] = None) -> str:
        """
        Emit an agent lifecycle event.

        Args:
            event_type: Lifecycle event type
            agent_id: Agent identifier
            profile: Agent profile
            trace_id: Trace ID

        Returns:
            Event ID
        """
        attributes = {
            'agent_name': profile.get('name'),
            'agent_version': profile.get('version'),
            'node_count': len(profile.get('nodes', [])),
            'routing_strategy': profile.get('routing_strategy'),
            'clearance_level': profile.get('policy_bindings', {}).get('clearance_level')
        }

        return self.emit_event(
            event_type=event_type,
            agent_id=agent_id,
            attributes=attributes,
            trace_id=trace_id
        )

    def emit_delegation_event(self, event_type: EventType, agent_id: str,
                             requester_id: str, node_id: str,
                             delegation_depth: int,
                             duration_ms: Optional[float] = None,
                             error: Optional[str] = None,
                             trace_id: Optional[str] = None,
                             span_id: Optional[str] = None,
                             parent_span_id: Optional[str] = None) -> str:
        """
        Emit a delegation event.

        Args:
            event_type: Delegation event type
            agent_id: Agent identifier
            requester_id: Requester identifier
            node_id: Target node identifier
            delegation_depth: Current delegation depth
            duration_ms: Operation duration
            error: Error message if failed
            trace_id: Trace ID
            span_id: Span ID
            parent_span_id: Parent span ID

        Returns:
            Event ID
        """
        attributes = {
            'node_id': node_id,
            'delegation_depth': delegation_depth,
            'duration_ms': duration_ms,
            'error_message': error
        }

        return self.emit_event(
            event_type=event_type,
            agent_id=agent_id,
            requester_id=requester_id,
            attributes=attributes,
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id
        )

    def emit_clearance_event(self, event_type: EventType, agent_id: str,
                            requester_id: str, agent_clearance: str,
                            requester_clearance: str, is_escalation: bool,
                            policy_decision: str,
                            matched_policies: List[str],
                            trace_id: Optional[str] = None) -> str:
        """
        Emit a clearance check event.

        Args:
            event_type: Clearance event type
            agent_id: Agent identifier
            requester_id: Requester identifier
            agent_clearance: Agent clearance level
            requester_clearance: Requester clearance level
            is_escalation: Whether this is an escalation
            policy_decision: Policy decision (allow/deny)
            matched_policies: List of matched policy IDs
            trace_id: Trace ID

        Returns:
            Event ID
        """
        attributes = {
            'clearance_level': agent_clearance,
            'requester_clearance': requester_clearance,
            'is_escalation': is_escalation,
            'policy_decision': policy_decision,
            'matched_policies': matched_policies
        }

        security_context = {
            'clearance_escalation': is_escalation,
            'policy_violations': [] if policy_decision == 'allow' else matched_policies
        }

        return self.emit_event(
            event_type=event_type,
            agent_id=agent_id,
            requester_id=requester_id,
            attributes=attributes,
            security_context=security_context,
            trace_id=trace_id
        )

    def emit_redaction_event(self, agent_id: str, requester_id: str,
                            items_redacted: int, filters_applied: List[str],
                            attestation_hash: str,
                            trace_id: Optional[str] = None) -> str:
        """
        Emit a redaction event.

        Args:
            agent_id: Agent identifier
            requester_id: Requester identifier
            items_redacted: Number of items redacted
            filters_applied: List of filters applied
            attestation_hash: Attestation hash
            trace_id: Trace ID

        Returns:
            Event ID
        """
        attributes = {
            'items_redacted': items_redacted,
            'filters_applied': filters_applied
        }

        security_context = {
            'redaction_applied': True,
            'attestation_hash': attestation_hash
        }

        return self.emit_event(
            event_type=EventType.REDACTION_APPLIED,
            agent_id=agent_id,
            requester_id=requester_id,
            attributes=attributes,
            security_context=security_context,
            trace_id=trace_id
        )

    def emit_policy_event(self, event_type: EventType, agent_id: str,
                         requester_id: str, policy_decision: str,
                         matched_policies: List[str],
                         violations: Optional[List[str]] = None,
                         trace_id: Optional[str] = None) -> str:
        """
        Emit a policy evaluation event.

        Args:
            event_type: Policy event type
            agent_id: Agent identifier
            requester_id: Requester identifier
            policy_decision: Decision (allow/deny)
            matched_policies: Matched policy IDs
            violations: Policy violations if any
            trace_id: Trace ID

        Returns:
            Event ID
        """
        attributes = {
            'policy_decision': policy_decision,
            'matched_policies': matched_policies
        }

        security_context = {
            'policy_violations': violations or []
        }

        return self.emit_event(
            event_type=event_type,
            agent_id=agent_id,
            requester_id=requester_id,
            attributes=attributes,
            security_context=security_context,
            trace_id=trace_id
        )

    def emit_composition_event(self, event_type: EventType, agent_id: str,
                              duration_ms: float,
                              steps_completed: int,
                              steps_failed: int,
                              error: Optional[str] = None,
                              trace_id: Optional[str] = None) -> str:
        """
        Emit a composition event.

        Args:
            event_type: Composition event type
            agent_id: Agent identifier
            duration_ms: Composition duration
            steps_completed: Number of steps completed
            steps_failed: Number of steps failed
            error: Error message if failed
            trace_id: Trace ID

        Returns:
            Event ID
        """
        attributes = {
            'duration_ms': duration_ms,
            'steps_completed': steps_completed,
            'steps_failed': steps_failed,
            'error_message': error
        }

        return self.emit_event(
            event_type=event_type,
            agent_id=agent_id,
            attributes=attributes,
            trace_id=trace_id
        )

    def _generate_trace_id(self) -> str:
        """Generate a trace ID."""
        return f"trace-{uuid.uuid4().hex[:16]}"

    def _generate_span_id(self) -> str:
        """Generate a span ID."""
        return f"span-{uuid.uuid4().hex[:8]}"

    def get_events(self, agent_id: Optional[str] = None,
                   event_type: Optional[EventType] = None,
                   limit: int = 100) -> List[Dict]:
        """
        Get collected events with optional filtering.

        Args:
            agent_id: Filter by agent ID
            event_type: Filter by event type
            limit: Maximum number of events to return

        Returns:
            List of events
        """
        filtered = self.events

        if agent_id:
            filtered = [e for e in filtered if e['agent_id'] == agent_id]

        if event_type:
            filtered = [e for e in filtered if e['event_type'] == event_type.value]

        return filtered[-limit:]

    def clear_events(self) -> None:
        """Clear collected events."""
        self.events.clear()

    def add_exporter(self, exporter: Any) -> None:
        """Add a telemetry exporter."""
        self.exporters.append(exporter)

    def remove_exporter(self, exporter: Any) -> None:
        """Remove a telemetry exporter."""
        self.exporters.remove(exporter)
