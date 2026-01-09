"""Event Bus

Provides pub/sub event bus for loose coupling between components.
"""

from typing import Callable, Dict, List, Any
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class EventBus:
    """
    Simple event bus for component communication.

    Components can publish events and subscribe to event types
    without direct dependencies.
    """

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable):
        """
        Subscribe to an event type.

        Args:
            event_type: Event type to subscribe to
            handler: Callback function(event_data)
        """
        self.subscribers[event_type].append(handler)
        logger.debug(f"Subscribed to {event_type}")

    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from an event type"""
        if handler in self.subscribers[event_type]:
            self.subscribers[event_type].remove(handler)

    def publish(self, event_type: str, event_data: Any):
        """
        Publish an event.

        Args:
            event_type: Event type
            event_data: Event data
        """
        logger.debug(f"Publishing {event_type}")

        for handler in self.subscribers[event_type]:
            try:
                handler(event_data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")


# Global event bus
_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Get global event bus"""
    return _event_bus


# Standard event types
class EventTypes:
    """Standard event type constants"""

    # Deployment events
    SERVICE_DEPLOYED = "service.deployed"
    SERVICE_REMOVED = "service.removed"
    SERVICE_MIGRATED = "service.migrated"

    # Mesh events
    SERVICE_REGISTERED = "mesh.service.registered"
    ROUTE_COMPUTED = "mesh.route.computed"

    # Replication events
    REPLICA_ADDED = "replication.replica.added"
    REPLICA_REMOVED = "replication.replica.removed"

    # Scheduler events
    CURVATURE_UPDATED = "scheduler.curvature.updated"
    AUTOSCALE_TRIGGERED = "scheduler.autoscale.triggered"

    # Governance events
    CHANGE_REQUESTED = "governance.change.requested"
    CHANGE_APPROVED = "governance.change.approved"
    CHANGE_REJECTED = "governance.change.rejected"
    FREEZE_ACTIVATED = "governance.freeze.activated"

    # Policy events
    POLICY_VIOLATION = "policy.violation"
    POLICY_UPDATED = "policy.updated"

    # Token events
    TOKEN_LIMIT_EXCEEDED = "token.limit.exceeded"
    BUDGET_EXHAUSTED = "budget.exhausted"
