"""
Event Subscription Hub - Subscribe to database change streams.

Enables agents to subscribe to database change events with throttling
and filtering capabilities.
"""
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import asyncio


class EventType(Enum):
    """Database event types."""
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    SCHEMA_CHANGE = "schema_change"


@dataclass
class DatabaseEvent:
    """Database change event."""
    event_id: str
    event_type: EventType
    relation: str
    data: Dict[str, Any]
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class Subscription:
    """Event subscription."""
    subscription_id: str
    agent_id: str
    event_types: List[EventType]
    relations: List[str]
    callback: Callable
    throttle_ms: int
    created_at: datetime
    last_triggered: Optional[datetime] = None


class EventSubscriptionHub:
    """
    Event subscription hub for database change streams.

    Allows agents to subscribe to specific event types and relations
    with throttling to prevent overwhelming subscribers.
    """

    def __init__(self):
        self.subscriptions: Dict[str, Subscription] = {}
        self.event_queue: List[DatabaseEvent] = []
        self.processing_task: Optional[asyncio.Task] = None

    async def subscribe(
        self,
        agent_id: str,
        event_types: List[EventType],
        relations: List[str],
        callback: Callable,
        throttle_ms: int = 1000
    ) -> str:
        """
        Subscribe to database events.

        Args:
            agent_id: Agent identifier
            event_types: List of event types to subscribe to
            relations: List of relations to monitor
            callback: Callback function for events
            throttle_ms: Minimum milliseconds between notifications

        Returns:
            Subscription ID
        """
        subscription_id = f"sub_{agent_id}_{int(datetime.now().timestamp())}"

        subscription = Subscription(
            subscription_id=subscription_id,
            agent_id=agent_id,
            event_types=event_types,
            relations=relations,
            callback=callback,
            throttle_ms=throttle_ms,
            created_at=datetime.now()
        )

        self.subscriptions[subscription_id] = subscription

        # Start processing task if not running
        if not self.processing_task:
            self.processing_task = asyncio.create_task(self._process_events())

        return subscription_id

    async def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events.

        Args:
            subscription_id: Subscription identifier

        Returns:
            True if unsubscribed successfully
        """
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
            return True
        return False

    async def emit_event(
        self,
        event_type: EventType,
        relation: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Emit database event to subscribers.

        Args:
            event_type: Type of event
            relation: Affected relation
            data: Event data
            metadata: Optional metadata
        """
        event_id = f"evt_{relation}_{int(datetime.now().timestamp())}"

        event = DatabaseEvent(
            event_id=event_id,
            event_type=event_type,
            relation=relation,
            data=data,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )

        self.event_queue.append(event)

    async def _process_events(self) -> None:
        """Process event queue and notify subscribers."""
        while True:
            if not self.event_queue:
                await asyncio.sleep(0.1)
                continue

            event = self.event_queue.pop(0)

            # Find matching subscriptions
            for subscription in self.subscriptions.values():
                if self._matches_subscription(event, subscription):
                    # Check throttle
                    if self._should_throttle(subscription):
                        continue

                    # Notify subscriber
                    try:
                        await subscription.callback(event)
                        subscription.last_triggered = datetime.now()
                    except Exception as e:
                        # Log error but continue processing
                        print(f"Error in subscription callback: {e}")

            await asyncio.sleep(0.01)

    def _matches_subscription(self, event: DatabaseEvent, subscription: Subscription) -> bool:
        """Check if event matches subscription criteria."""
        if event.event_type not in subscription.event_types:
            return False

        if subscription.relations and event.relation not in subscription.relations:
            return False

        return True

    def _should_throttle(self, subscription: Subscription) -> bool:
        """Check if subscription should be throttled."""
        if not subscription.last_triggered:
            return False

        elapsed = (datetime.now() - subscription.last_triggered).total_seconds() * 1000
        return elapsed < subscription.throttle_ms

    def get_subscription_stats(self) -> Dict[str, Any]:
        """Get subscription statistics."""
        return {
            "total_subscriptions": len(self.subscriptions),
            "queue_size": len(self.event_queue),
            "subscriptions_by_agent": self._count_by_agent()
        }

    def _count_by_agent(self) -> Dict[str, int]:
        """Count subscriptions by agent."""
        counts = {}
        for sub in self.subscriptions.values():
            counts[sub.agent_id] = counts.get(sub.agent_id, 0) + 1
        return counts
