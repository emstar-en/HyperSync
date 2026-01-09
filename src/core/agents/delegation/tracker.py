"""
HyperSync Delegation Chain Tracker

Tracks agent delegation chains with depth limits, cycle detection, and visualization.
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DelegationStatus(Enum):
    """Delegation status."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class DelegationNode:
    """Represents a node in the delegation chain."""
    agent_id: str
    node_id: str
    depth: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: DelegationStatus = DelegationStatus.PENDING
    duration_ms: Optional[float] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'agent_id': self.agent_id,
            'node_id': self.node_id,
            'depth': self.depth,
            'started_at': self.started_at.isoformat() + 'Z',
            'completed_at': self.completed_at.isoformat() + 'Z' if self.completed_at else None,
            'status': self.status.value,
            'duration_ms': self.duration_ms,
            'error': self.error,
            'metadata': self.metadata
        }


@dataclass
class DelegationChain:
    """Represents a complete delegation chain."""
    chain_id: str
    requester_id: str
    root_agent_id: str
    nodes: List[DelegationNode] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    status: DelegationStatus = DelegationStatus.PENDING
    max_depth: int = 10

    def add_node(self, agent_id: str, node_id: str) -> DelegationNode:
        """
        Add a node to the delegation chain.

        Args:
            agent_id: Agent identifier
            node_id: Node identifier

        Returns:
            Created delegation node
        """
        depth = len(self.nodes)

        if depth >= self.max_depth:
            raise ValueError(f"Maximum delegation depth ({self.max_depth}) exceeded")

        node = DelegationNode(
            agent_id=agent_id,
            node_id=node_id,
            depth=depth,
            started_at=datetime.utcnow()
        )

        self.nodes.append(node)
        logger.debug(f"Added delegation node: {agent_id} -> {node_id} (depth: {depth})")

        return node

    def complete_node(self, node_index: int, duration_ms: float,
                     error: Optional[str] = None) -> None:
        """
        Mark a node as completed.

        Args:
            node_index: Index of node to complete
            duration_ms: Duration in milliseconds
            error: Optional error message
        """
        if node_index >= len(self.nodes):
            raise IndexError(f"Node index {node_index} out of range")

        node = self.nodes[node_index]
        node.completed_at = datetime.utcnow()
        node.duration_ms = duration_ms
        node.status = DelegationStatus.FAILED if error else DelegationStatus.COMPLETED
        node.error = error

        logger.debug(f"Completed delegation node {node_index}: {node.status.value}")

    def get_current_depth(self) -> int:
        """Get current delegation depth."""
        return len(self.nodes)

    def get_agent_ids(self) -> List[str]:
        """Get list of agent IDs in chain."""
        return [node.agent_id for node in self.nodes]

    def has_cycle(self) -> bool:
        """Check if chain contains a cycle."""
        agent_ids = self.get_agent_ids()
        return len(agent_ids) != len(set(agent_ids))

    def get_cycle_agents(self) -> List[str]:
        """Get agents involved in cycle."""
        if not self.has_cycle():
            return []

        seen: Set[str] = set()
        cycle_agents: List[str] = []

        for agent_id in self.get_agent_ids():
            if agent_id in seen:
                cycle_agents.append(agent_id)
            seen.add(agent_id)

        return cycle_agents

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'chain_id': self.chain_id,
            'requester_id': self.requester_id,
            'root_agent_id': self.root_agent_id,
            'nodes': [node.to_dict() for node in self.nodes],
            'created_at': self.created_at.isoformat() + 'Z',
            'completed_at': self.completed_at.isoformat() + 'Z' if self.completed_at else None,
            'status': self.status.value,
            'max_depth': self.max_depth,
            'current_depth': self.get_current_depth(),
            'has_cycle': self.has_cycle()
        }


class DelegationChainTracker:
    """
    Tracks active and historical delegation chains.

    Provides cycle detection, depth limiting, and chain visualization.
    """

    def __init__(self, max_depth: int = 10, max_active_chains: int = 1000):
        """
        Initialize delegation chain tracker.

        Args:
            max_depth: Maximum delegation depth
            max_active_chains: Maximum number of active chains to track
        """
        self.max_depth = max_depth
        self.max_active_chains = max_active_chains
        self.active_chains: Dict[str, DelegationChain] = {}
        self.completed_chains: List[DelegationChain] = []

    def start_chain(self, chain_id: str, requester_id: str,
                   root_agent_id: str) -> DelegationChain:
        """
        Start a new delegation chain.

        Args:
            chain_id: Unique chain identifier
            requester_id: Original requester
            root_agent_id: Root agent starting the chain

        Returns:
            Created delegation chain
        """
        if len(self.active_chains) >= self.max_active_chains:
            raise RuntimeError(f"Maximum active chains ({self.max_active_chains}) exceeded")

        chain = DelegationChain(
            chain_id=chain_id,
            requester_id=requester_id,
            root_agent_id=root_agent_id,
            max_depth=self.max_depth
        )

        self.active_chains[chain_id] = chain
        logger.info(f"Started delegation chain: {chain_id}")

        return chain

    def add_delegation(self, chain_id: str, agent_id: str,
                      node_id: str) -> DelegationNode:
        """
        Add a delegation to an active chain.

        Args:
            chain_id: Chain identifier
            agent_id: Agent identifier
            node_id: Node identifier

        Returns:
            Created delegation node
        """
        chain = self.active_chains.get(chain_id)
        if not chain:
            raise ValueError(f"Chain {chain_id} not found")

        # Check for cycles
        if agent_id in chain.get_agent_ids():
            logger.warning(f"Cycle detected in chain {chain_id}: {agent_id}")
            raise ValueError(f"Cycle detected: agent {agent_id} already in chain")

        return chain.add_node(agent_id, node_id)

    def complete_delegation(self, chain_id: str, node_index: int,
                          duration_ms: float, error: Optional[str] = None) -> None:
        """
        Mark a delegation as completed.

        Args:
            chain_id: Chain identifier
            node_index: Node index
            duration_ms: Duration
            error: Optional error
        """
        chain = self.active_chains.get(chain_id)
        if not chain:
            raise ValueError(f"Chain {chain_id} not found")

        chain.complete_node(node_index, duration_ms, error)

    def complete_chain(self, chain_id: str) -> DelegationChain:
        """
        Mark a chain as completed and archive it.

        Args:
            chain_id: Chain identifier

        Returns:
            Completed chain
        """
        chain = self.active_chains.pop(chain_id, None)
        if not chain:
            raise ValueError(f"Chain {chain_id} not found")

        chain.completed_at = datetime.utcnow()
        chain.status = DelegationStatus.COMPLETED

        self.completed_chains.append(chain)
        logger.info(f"Completed delegation chain: {chain_id}")

        return chain

    def get_chain(self, chain_id: str) -> Optional[DelegationChain]:
        """Get a chain by ID (active or completed)."""
        if chain_id in self.active_chains:
            return self.active_chains[chain_id]

        for chain in self.completed_chains:
            if chain.chain_id == chain_id:
                return chain

        return None

    def get_active_chains(self) -> List[DelegationChain]:
        """Get all active chains."""
        return list(self.active_chains.values())

    def get_chains_by_requester(self, requester_id: str) -> List[DelegationChain]:
        """Get all chains for a requester."""
        chains = []

        # Active chains
        for chain in self.active_chains.values():
            if chain.requester_id == requester_id:
                chains.append(chain)

        # Completed chains
        for chain in self.completed_chains:
            if chain.requester_id == requester_id:
                chains.append(chain)

        return chains

    def get_chains_by_agent(self, agent_id: str) -> List[DelegationChain]:
        """Get all chains involving an agent."""
        chains = []

        for chain in self.active_chains.values():
            if agent_id in chain.get_agent_ids():
                chains.append(chain)

        for chain in self.completed_chains:
            if agent_id in chain.get_agent_ids():
                chains.append(chain)

        return chains

    def get_stats(self) -> Dict[str, Any]:
        """Get tracker statistics."""
        total_chains = len(self.active_chains) + len(self.completed_chains)

        total_delegations = sum(
            len(chain.nodes) for chain in self.active_chains.values()
        ) + sum(
            len(chain.nodes) for chain in self.completed_chains
        )

        cycles_detected = sum(
            1 for chain in self.completed_chains if chain.has_cycle()
        )

        return {
            'active_chains': len(self.active_chains),
            'completed_chains': len(self.completed_chains),
            'total_chains': total_chains,
            'total_delegations': total_delegations,
            'cycles_detected': cycles_detected,
            'max_depth': self.max_depth,
            'max_active_chains': self.max_active_chains
        }
