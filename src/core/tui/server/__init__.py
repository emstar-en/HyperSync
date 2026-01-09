"""
HyperSync TUI Server

Async TUI server hub for state broadcasting, session lifecycle, and auth hooks.
"""

import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any
from datetime import datetime
import uuid


logger = logging.getLogger(__name__)


class TUISession:
    """Represents a single TUI session."""

    def __init__(self, session_id: str, operator_id: str, capabilities: Dict[str, Any]):
        self.session_id = session_id
        self.operator_id = operator_id
        self.capabilities = capabilities
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.state = {}
        self.subscribers = set()

    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize session to dictionary."""
        return {
            "session_id": self.session_id,
            "operator_id": self.operator_id,
            "capabilities": self.capabilities,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "state": self.state
        }


class SessionHub:
    """
    Central hub for managing TUI sessions.

    Handles session lifecycle, state broadcasting, and pub/sub channels.
    """

    def __init__(self):
        self.sessions: Dict[str, TUISession] = {}
        self.channels: Dict[str, Set[str]] = {}  # channel_name -> session_ids
        self.message_queues: Dict[str, asyncio.Queue] = {}
        self._lock = asyncio.Lock()
        logger.info("SessionHub initialized")

    async def create_session(
        self, 
        operator_id: str, 
        capabilities: Dict[str, Any],
        auth_token: Optional[str] = None
    ) -> str:
        """
        Create a new TUI session.

        Args:
            operator_id: Operator identifier
            capabilities: Client capabilities
            auth_token: Optional authentication token

        Returns:
            Session ID
        """
        async with self._lock:
            session_id = str(uuid.uuid4())

            # TODO: Validate auth_token if provided

            session = TUISession(session_id, operator_id, capabilities)
            self.sessions[session_id] = session
            self.message_queues[session_id] = asyncio.Queue()

            logger.info(f"Created session {session_id} for operator {operator_id}")

            return session_id

    async def destroy_session(self, session_id: str):
        """Destroy a TUI session."""
        async with self._lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]

                # Unsubscribe from all channels
                for channel_name, subscribers in self.channels.items():
                    subscribers.discard(session_id)

                # Clean up
                del self.sessions[session_id]
                del self.message_queues[session_id]

                logger.info(f"Destroyed session {session_id} for operator {session.operator_id}")

    async def get_session(self, session_id: str) -> Optional[TUISession]:
        """Get session by ID."""
        return self.sessions.get(session_id)

    async def update_session_state(self, session_id: str, state: Dict[str, Any]):
        """Update session state."""
        async with self._lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                session.state.update(state)
                session.update_activity()

                # Broadcast state update to subscribers
                await self._broadcast_to_session(session_id, {
                    "type": "state_update",
                    "state": state,
                    "timestamp": datetime.utcnow().isoformat()
                })

    async def subscribe(self, session_id: str, channel_name: str):
        """Subscribe session to a channel."""
        async with self._lock:
            if channel_name not in self.channels:
                self.channels[channel_name] = set()

            self.channels[channel_name].add(session_id)
            logger.debug(f"Session {session_id} subscribed to {channel_name}")

    async def unsubscribe(self, session_id: str, channel_name: str):
        """Unsubscribe session from a channel."""
        async with self._lock:
            if channel_name in self.channels:
                self.channels[channel_name].discard(session_id)
                logger.debug(f"Session {session_id} unsubscribed from {channel_name}")

    async def broadcast(self, channel_name: str, message: Dict[str, Any]):
        """
        Broadcast message to all subscribers of a channel.

        Args:
            channel_name: Channel to broadcast to
            message: Message payload
        """
        if channel_name not in self.channels:
            return

        subscribers = self.channels[channel_name].copy()

        for session_id in subscribers:
            await self._broadcast_to_session(session_id, message)

    async def _broadcast_to_session(self, session_id: str, message: Dict[str, Any]):
        """Send message to specific session."""
        if session_id in self.message_queues:
            await self.message_queues[session_id].put(message)

    async def get_messages(self, session_id: str, timeout: float = 1.0) -> list:
        """
        Get pending messages for a session.

        Args:
            session_id: Session ID
            timeout: Timeout in seconds

        Returns:
            List of messages
        """
        if session_id not in self.message_queues:
            return []

        messages = []
        queue = self.message_queues[session_id]

        try:
            # Get first message with timeout
            message = await asyncio.wait_for(queue.get(), timeout=timeout)
            messages.append(message)

            # Get any additional messages without blocking
            while not queue.empty():
                messages.append(queue.get_nowait())

        except asyncio.TimeoutError:
            pass

        return messages

    async def list_sessions(self) -> list:
        """List all active sessions."""
        return [session.to_dict() for session in self.sessions.values()]

    async def cleanup_inactive_sessions(self, timeout_seconds: int = 3600):
        """Clean up inactive sessions."""
        now = datetime.utcnow()
        inactive_sessions = []

        for session_id, session in self.sessions.items():
            elapsed = (now - session.last_activity).total_seconds()
            if elapsed > timeout_seconds:
                inactive_sessions.append(session_id)

        for session_id in inactive_sessions:
            await self.destroy_session(session_id)
            logger.info(f"Cleaned up inactive session {session_id}")


# Global session hub instance
_session_hub = None


def get_session_hub() -> SessionHub:
    """Get global session hub instance."""
    global _session_hub
    if _session_hub is None:
        _session_hub = SessionHub()
    return _session_hub
