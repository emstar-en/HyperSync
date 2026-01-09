"""
Cross-Agent Collaboration Manager - Shared knowledge bases with ACLs.

Enables agents to share knowledge bases with fine-grained access control
and conflict resolution for concurrent updates.
"""
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio


class AccessLevel(Enum):
    """Access control levels."""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


@dataclass
class KnowledgeBase:
    """Shared knowledge base."""
    kb_id: str
    name: str
    owner_agent_id: str
    created_at: datetime
    records: Dict[str, Any]
    access_control: Dict[str, AccessLevel]  # agent_id -> access_level


@dataclass
class CollaborationEvent:
    """Collaboration event log."""
    event_id: str
    kb_id: str
    agent_id: str
    action: str
    timestamp: datetime
    metadata: Dict[str, Any]


class CollaborationManager:
    """
    Cross-agent collaboration manager.

    Manages shared knowledge bases with access control lists and
    conflict resolution for concurrent agent updates.
    """

    def __init__(self):
        self.knowledge_bases: Dict[str, KnowledgeBase] = {}
        self.events: List[CollaborationEvent] = []
        self.locks: Dict[str, asyncio.Lock] = {}

    async def create_knowledge_base(
        self,
        owner_agent_id: str,
        name: str,
        initial_acl: Optional[Dict[str, AccessLevel]] = None
    ) -> KnowledgeBase:
        """
        Create new shared knowledge base.

        Args:
            owner_agent_id: Owner agent ID
            name: Knowledge base name
            initial_acl: Initial access control list

        Returns:
            Created KnowledgeBase
        """
        kb_id = f"kb_{owner_agent_id}_{int(datetime.now().timestamp())}"

        acl = initial_acl or {}
        acl[owner_agent_id] = AccessLevel.ADMIN

        kb = KnowledgeBase(
            kb_id=kb_id,
            name=name,
            owner_agent_id=owner_agent_id,
            created_at=datetime.now(),
            records={},
            access_control=acl
        )

        self.knowledge_bases[kb_id] = kb
        self.locks[kb_id] = asyncio.Lock()

        await self._log_event(kb_id, owner_agent_id, "create", {"name": name})

        return kb

    async def grant_access(
        self,
        kb_id: str,
        requesting_agent_id: str,
        target_agent_id: str,
        access_level: AccessLevel
    ) -> bool:
        """
        Grant access to knowledge base.

        Args:
            kb_id: Knowledge base ID
            requesting_agent_id: Agent requesting the grant
            target_agent_id: Agent to grant access to
            access_level: Access level to grant

        Returns:
            True if access granted successfully
        """
        if kb_id not in self.knowledge_bases:
            return False

        kb = self.knowledge_bases[kb_id]

        # Check if requesting agent has admin access
        if kb.access_control.get(requesting_agent_id) != AccessLevel.ADMIN:
            return False

        kb.access_control[target_agent_id] = access_level

        await self._log_event(
            kb_id,
            requesting_agent_id,
            "grant_access",
            {"target_agent": target_agent_id, "level": access_level.value}
        )

        return True

    async def revoke_access(
        self,
        kb_id: str,
        requesting_agent_id: str,
        target_agent_id: str
    ) -> bool:
        """
        Revoke access to knowledge base.

        Args:
            kb_id: Knowledge base ID
            requesting_agent_id: Agent requesting the revocation
            target_agent_id: Agent to revoke access from

        Returns:
            True if access revoked successfully
        """
        if kb_id not in self.knowledge_bases:
            return False

        kb = self.knowledge_bases[kb_id]

        # Check if requesting agent has admin access
        if kb.access_control.get(requesting_agent_id) != AccessLevel.ADMIN:
            return False

        # Cannot revoke owner's access
        if target_agent_id == kb.owner_agent_id:
            return False

        kb.access_control.pop(target_agent_id, None)

        await self._log_event(
            kb_id,
            requesting_agent_id,
            "revoke_access",
            {"target_agent": target_agent_id}
        )

        return True

    async def write_record(
        self,
        kb_id: str,
        agent_id: str,
        key: str,
        value: Any
    ) -> bool:
        """
        Write record to knowledge base with conflict resolution.

        Args:
            kb_id: Knowledge base ID
            agent_id: Agent ID
            key: Record key
            value: Record value

        Returns:
            True if write successful
        """
        if kb_id not in self.knowledge_bases:
            return False

        kb = self.knowledge_bases[kb_id]

        # Check write permission
        access = kb.access_control.get(agent_id, AccessLevel.NONE)
        if access not in [AccessLevel.WRITE, AccessLevel.ADMIN]:
            return False

        # Acquire lock for conflict resolution
        async with self.locks[kb_id]:
            # Check for conflicts
            if key in kb.records:
                # Conflict detected - use last-write-wins strategy
                await self._log_event(
                    kb_id,
                    agent_id,
                    "conflict_resolved",
                    {"key": key, "strategy": "last-write-wins"}
                )

            kb.records[key] = {
                "value": value,
                "updated_by": agent_id,
                "updated_at": datetime.now()
            }

        await self._log_event(kb_id, agent_id, "write", {"key": key})

        return True

    async def read_record(
        self,
        kb_id: str,
        agent_id: str,
        key: str
    ) -> Optional[Any]:
        """
        Read record from knowledge base.

        Args:
            kb_id: Knowledge base ID
            agent_id: Agent ID
            key: Record key

        Returns:
            Record value or None
        """
        if kb_id not in self.knowledge_bases:
            return None

        kb = self.knowledge_bases[kb_id]

        # Check read permission
        access = kb.access_control.get(agent_id, AccessLevel.NONE)
        if access == AccessLevel.NONE:
            return None

        record = kb.records.get(key)
        if record:
            await self._log_event(kb_id, agent_id, "read", {"key": key})
            return record["value"]

        return None

    async def list_knowledge_bases(self, agent_id: str) -> List[KnowledgeBase]:
        """
        List knowledge bases accessible to agent.

        Args:
            agent_id: Agent ID

        Returns:
            List of accessible knowledge bases
        """
        accessible = []

        for kb in self.knowledge_bases.values():
            if agent_id in kb.access_control:
                accessible.append(kb)

        return accessible

    async def get_collaboration_events(
        self,
        kb_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 100
    ) -> List[CollaborationEvent]:
        """
        Get collaboration events with optional filters.

        Args:
            kb_id: Filter by knowledge base ID
            agent_id: Filter by agent ID
            limit: Maximum number of events

        Returns:
            List of collaboration events
        """
        events = self.events

        if kb_id:
            events = [e for e in events if e.kb_id == kb_id]

        if agent_id:
            events = [e for e in events if e.agent_id == agent_id]

        return events[-limit:]

    async def _log_event(
        self,
        kb_id: str,
        agent_id: str,
        action: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log collaboration event."""
        event_id = f"evt_{kb_id}_{int(datetime.now().timestamp())}"

        event = CollaborationEvent(
            event_id=event_id,
            kb_id=kb_id,
            agent_id=agent_id,
            action=action,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )

        self.events.append(event)
