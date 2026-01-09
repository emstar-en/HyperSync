"""
HyperSync TUI Collaboration Manager

Multi-operator presence, baton passing, and session sharing.
"""

import logging
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto


logger = logging.getLogger(__name__)


class PresenceStatus(Enum):
    """Operator presence status."""
    ACTIVE = auto()
    IDLE = auto()
    AWAY = auto()


@dataclass
class OperatorPresence:
    """Operator presence information."""
    operator_id: str
    session_id: str
    status: PresenceStatus
    active_panel: Optional[str]
    cursor_position: Optional[tuple]
    last_activity: datetime


class CollaborationManager:
    """
    Collaboration manager.

    Manages multi-operator presence, baton control, and conflict resolution.
    """

    def __init__(self):
        self.presences: Dict[str, OperatorPresence] = {}
        self.baton_holder: Optional[str] = None
        self.shared_sessions: Dict[str, Set[str]] = {}  # session_id -> operator_ids
        logger.info("CollaborationManager initialized")

    def add_operator(
        self,
        operator_id: str,
        session_id: str
    ) -> OperatorPresence:
        """
        Add operator to collaboration session.

        Args:
            operator_id: Operator ID
            session_id: Session ID

        Returns:
            Operator presence
        """
        presence = OperatorPresence(
            operator_id=operator_id,
            session_id=session_id,
            status=PresenceStatus.ACTIVE,
            active_panel=None,
            cursor_position=None,
            last_activity=datetime.utcnow()
        )

        self.presences[operator_id] = presence

        if session_id not in self.shared_sessions:
            self.shared_sessions[session_id] = set()

        self.shared_sessions[session_id].add(operator_id)

        logger.info(f"Added operator {operator_id} to session {session_id}")

        return presence

    def remove_operator(self, operator_id: str):
        """Remove operator from collaboration."""
        if operator_id in self.presences:
            presence = self.presences[operator_id]
            session_id = presence.session_id

            del self.presences[operator_id]

            if session_id in self.shared_sessions:
                self.shared_sessions[session_id].discard(operator_id)

            # Release baton if held
            if self.baton_holder == operator_id:
                self.baton_holder = None

            logger.info(f"Removed operator {operator_id}")

    def update_presence(
        self,
        operator_id: str,
        status: Optional[PresenceStatus] = None,
        active_panel: Optional[str] = None,
        cursor_position: Optional[tuple] = None
    ):
        """Update operator presence."""
        if operator_id in self.presences:
            presence = self.presences[operator_id]

            if status:
                presence.status = status

            if active_panel:
                presence.active_panel = active_panel

            if cursor_position:
                presence.cursor_position = cursor_position

            presence.last_activity = datetime.utcnow()

    def request_baton(self, operator_id: str) -> bool:
        """
        Request baton control.

        Args:
            operator_id: Operator ID

        Returns:
            True if baton granted
        """
        if self.baton_holder is None:
            self.baton_holder = operator_id
            logger.info(f"Baton granted to {operator_id}")
            return True

        return False

    def release_baton(self, operator_id: str) -> bool:
        """
        Release baton control.

        Args:
            operator_id: Operator ID

        Returns:
            True if baton released
        """
        if self.baton_holder == operator_id:
            self.baton_holder = None
            logger.info(f"Baton released by {operator_id}")
            return True

        return False

    def handoff_baton(self, from_operator: str, to_operator: str) -> bool:
        """
        Hand off baton to another operator.

        Args:
            from_operator: Current baton holder
            to_operator: Target operator

        Returns:
            True if handoff successful
        """
        if self.baton_holder == from_operator and to_operator in self.presences:
            self.baton_holder = to_operator
            logger.info(f"Baton handed off from {from_operator} to {to_operator}")
            return True

        return False

    def get_session_operators(self, session_id: str) -> List[str]:
        """Get operators in session."""
        return list(self.shared_sessions.get(session_id, set()))

    def get_presence(self, operator_id: str) -> Optional[OperatorPresence]:
        """Get operator presence."""
        return self.presences.get(operator_id)

    def list_presences(self) -> List[OperatorPresence]:
        """List all operator presences."""
        return list(self.presences.values())


# Global collaboration manager
_collaboration_manager = None


def get_collaboration_manager() -> CollaborationManager:
    """Get global collaboration manager."""
    global _collaboration_manager
    if _collaboration_manager is None:
        _collaboration_manager = CollaborationManager()
    return _collaboration_manager
