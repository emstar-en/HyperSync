"""
HyperSync WAN/Inter-Domain Mesh Coordinator

Orchestrates multi-hop dimensional alignment and TTL-limited state propagation
across wide-area and multi-tenant networks.
"""

import uuid
import time
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class TrustLevel(Enum):
    """Domain trust levels."""
    TRUSTED = "trusted"
    VERIFIED = "verified"
    UNTRUSTED = "untrusted"


class RouteStatus(Enum):
    """Route negotiation status."""
    PENDING = "pending"
    NEGOTIATING = "negotiating"
    ESTABLISHED = "established"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class Domain:
    """Represents a network domain."""
    domain_id: str
    node_ids: List[str]
    trust_level: TrustLevel = TrustLevel.VERIFIED

    def __hash__(self):
        return hash(self.domain_id)


@dataclass
class DimensionalContract:
    """
    Cross-domain dimensional sharing agreement.
    """
    contract_id: str
    source_domain: Domain
    target_domain: Domain
    shared_dimensions: List[int]
    max_hops: int
    ttl_seconds: int
    bandwidth_limit_mbps: Optional[int] = None
    latency_budget_ms: Optional[int] = None

    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    renewable: bool = False

    encryption_required: bool = True
    authentication_method: str = "mutual_tls"
    audit_level: str = "detailed"

    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    version: str = "1.0.0"

    def is_valid(self) -> bool:
        """Check if contract is currently valid."""
        now = datetime.now()
        if self.end_time and now > self.end_time:
            return False
        return now >= self.start_time

    def time_remaining(self) -> Optional[int]:
        """Get remaining validity time in seconds."""
        if not self.end_time:
            return None
        remaining = (self.end_time - datetime.now()).total_seconds()
        return max(0, int(remaining))

    def to_dict(self) -> Dict:
        """Export contract to dictionary."""
        return {
            "contract_id": self.contract_id,
            "domains": {
                "source": {
                    "domain_id": self.source_domain.domain_id,
                    "node_ids": self.source_domain.node_ids,
                    "trust_level": self.source_domain.trust_level.value
                },
                "target": {
                    "domain_id": self.target_domain.domain_id,
                    "node_ids": self.target_domain.node_ids,
                    "trust_level": self.target_domain.trust_level.value
                }
            },
            "dimensional_terms": {
                "shared_dimensions": self.shared_dimensions,
                "max_hops": self.max_hops,
                "ttl_seconds": self.ttl_seconds,
                "bandwidth_limit_mbps": self.bandwidth_limit_mbps,
                "latency_budget_ms": self.latency_budget_ms
            },
            "validity": {
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "renewable": self.renewable
            },
            "security": {
                "encryption_required": self.encryption_required,
                "authentication_method": self.authentication_method,
                "audit_level": self.audit_level
            },
            "metadata": {
                "created_at": self.created_at.isoformat(),
                "created_by": self.created_by,
                "version": self.version
            }
        }


@dataclass
class RouteHop:
    """Single hop in a multi-hop route."""
    hop_number: int
    domain_id: str
    node_id: str
    latency_ms: float = 0.0

    def __repr__(self):
        return f"Hop{self.hop_number}({self.domain_id}:{self.node_id})"


@dataclass
class MeshRoute:
    """Multi-hop route across domains."""
    route_id: str
    agent_id: str
    source_domain: str
    target_domain: str
    hops: List[RouteHop]
    dimensions: int
    contract_id: Optional[str] = None

    status: RouteStatus = RouteStatus.PENDING
    total_latency_ms: float = 0.0
    established_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    def hop_count(self) -> int:
        """Get number of hops in route."""
        return len(self.hops)

    def add_hop(self, domain_id: str, node_id: str, latency_ms: float = 0.0):
        """Add a hop to the route."""
        hop = RouteHop(
            hop_number=len(self.hops),
            domain_id=domain_id,
            node_id=node_id,
            latency_ms=latency_ms
        )
        self.hops.append(hop)
        self.total_latency_ms += latency_ms

    def to_dict(self) -> Dict:
        """Export route to dictionary."""
        return {
            "route_id": self.route_id,
            "agent_id": self.agent_id,
            "source_domain": self.source_domain,
            "target_domain": self.target_domain,
            "hops": [
                {
                    "hop_number": h.hop_number,
                    "domain_id": h.domain_id,
                    "node_id": h.node_id,
                    "latency_ms": h.latency_ms
                }
                for h in self.hops
            ],
            "dimensions": self.dimensions,
            "contract_id": self.contract_id,
            "status": self.status.value,
            "total_latency_ms": self.total_latency_ms,
            "established_at": self.established_at.isoformat() if self.established_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }


class MeshCoordinator:
    """
    Coordinates dimensional synchronization across WAN and multi-domain networks.

    Manages:
    - Cross-domain contracts
    - Multi-hop route negotiation
    - TTL-limited state propagation
    - Policy compliance
    """

    def __init__(self, capability_registry=None, policy_manager=None):
        self.capability_registry = capability_registry
        self.policy_manager = policy_manager

        self.contracts: Dict[str, DimensionalContract] = {}
        self.routes: Dict[str, MeshRoute] = {}
        self.domains: Dict[str, Domain] = {}

        # Topology graph: domain_id -> set of connected domain_ids
        self.topology: Dict[str, Set[str]] = {}

    def register_domain(self, domain: Domain):
        """Register a domain in the mesh."""
        self.domains[domain.domain_id] = domain
        if domain.domain_id not in self.topology:
            self.topology[domain.domain_id] = set()

    def create_contract(self, source_domain_id: str, target_domain_id: str,
                       shared_dims: List[int], max_hops: int = 3,
                       ttl_seconds: int = 3600, **kwargs) -> DimensionalContract:
        """
        Create a dimensional contract between domains.

        Args:
            source_domain_id: Source domain identifier
            target_domain_id: Target domain identifier
            shared_dims: Dimensions to share
            max_hops: Maximum routing hops
            ttl_seconds: Time-to-live for state propagation
            **kwargs: Additional contract parameters

        Returns:
            DimensionalContract instance
        """
        if source_domain_id not in self.domains:
            raise ValueError(f"Unknown source domain: {source_domain_id}")
        if target_domain_id not in self.domains:
            raise ValueError(f"Unknown target domain: {target_domain_id}")

        contract = DimensionalContract(
            contract_id=str(uuid.uuid4()),
            source_domain=self.domains[source_domain_id],
            target_domain=self.domains[target_domain_id],
            shared_dimensions=shared_dims,
            max_hops=max_hops,
            ttl_seconds=ttl_seconds,
            **kwargs
        )

        # Set end time based on TTL
        contract.end_time = contract.start_time + timedelta(seconds=ttl_seconds)

        self.contracts[contract.contract_id] = contract

        # Update topology
        self.topology[source_domain_id].add(target_domain_id)
        self.topology[target_domain_id].add(source_domain_id)

        return contract

    def get_contract(self, contract_id: str) -> Optional[DimensionalContract]:
        """Get contract by ID."""
        return self.contracts.get(contract_id)

    def list_contracts(self, domain_id: Optional[str] = None,
                      valid_only: bool = True) -> List[DimensionalContract]:
        """
        List contracts, optionally filtered by domain.

        Args:
            domain_id: Filter by domain (optional)
            valid_only: Only return valid contracts

        Returns:
            List of contracts
        """
        contracts = list(self.contracts.values())

        if domain_id:
            contracts = [
                c for c in contracts
                if c.source_domain.domain_id == domain_id or
                   c.target_domain.domain_id == domain_id
            ]

        if valid_only:
            contracts = [c for c in contracts if c.is_valid()]

        return contracts

    def negotiate_route(self, agent_id: str, target_domain: str,
                       dims: int, source_domain: Optional[str] = None) -> MeshRoute:
        """
        Negotiate a multi-hop route to target domain.

        Args:
            agent_id: Agent requesting route
            target_domain: Target domain identifier
            dims: Number of dimensions required
            source_domain: Source domain (auto-detect if None)

        Returns:
            MeshRoute instance
        """
        if not source_domain:
            # Auto-detect source domain (simplified)
            source_domain = list(self.domains.keys())[0] if self.domains else "default"

        route = MeshRoute(
            route_id=str(uuid.uuid4()),
            agent_id=agent_id,
            source_domain=source_domain,
            target_domain=target_domain,
            hops=[],
            dimensions=dims
        )

        # Find path using BFS
        path = self._find_path(source_domain, target_domain)

        if not path:
            route.status = RouteStatus.FAILED
            return route

        # Build route from path
        route.status = RouteStatus.NEGOTIATING

        for i, domain_id in enumerate(path):
            # Select node from domain (simplified - use first node)
            domain = self.domains.get(domain_id)
            if domain and domain.node_ids:
                node_id = domain.node_ids[0]
                # Simulate latency based on hop distance
                latency = 10.0 + (i * 5.0)  # Base 10ms + 5ms per hop
                route.add_hop(domain_id, node_id, latency)

        # Find applicable contract
        contract = self._find_contract(source_domain, target_domain, dims)
        if contract:
            route.contract_id = contract.contract_id
            route.expires_at = contract.end_time

        route.status = RouteStatus.ESTABLISHED
        route.established_at = datetime.now()

        self.routes[route.route_id] = route
        return route

    def _find_path(self, source: str, target: str, max_hops: int = 10) -> Optional[List[str]]:
        """Find shortest path between domains using BFS."""
        if source == target:
            return [source]

        if source not in self.topology or target not in self.topology:
            return None

        # BFS
        queue = [(source, [source])]
        visited = {source}

        while queue:
            current, path = queue.pop(0)

            if len(path) > max_hops:
                continue

            for neighbor in self.topology.get(current, set()):
                if neighbor == target:
                    return path + [neighbor]

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def _find_contract(self, source: str, target: str, dims: int) -> Optional[DimensionalContract]:
        """Find applicable contract for route."""
        for contract in self.contracts.values():
            if not contract.is_valid():
                continue

            if (contract.source_domain.domain_id == source and
                contract.target_domain.domain_id == target and
                len(contract.shared_dimensions) >= dims):
                return contract

        return None

    def execute_alignment(self, route: MeshRoute) -> bool:
        """
        Execute dimensional alignment along route.

        Args:
            route: Route to execute alignment on

        Returns:
            True if alignment successful
        """
        if route.status != RouteStatus.ESTABLISHED:
            return False

        # Verify contract validity
        if route.contract_id:
            contract = self.get_contract(route.contract_id)
            if not contract or not contract.is_valid():
                route.status = RouteStatus.EXPIRED
                return False

        # Execute alignment hop-by-hop (simulated)
        for hop in route.hops:
            # In production, this would trigger actual sync operations
            time.sleep(0.001)  # Simulate processing

        return True

    def get_route(self, route_id: str) -> Optional[MeshRoute]:
        """Get route by ID."""
        return self.routes.get(route_id)

    def cleanup_expired(self):
        """Remove expired contracts and routes."""
        # Remove expired contracts
        expired_contracts = [
            cid for cid, contract in self.contracts.items()
            if not contract.is_valid()
        ]
        for cid in expired_contracts:
            del self.contracts[cid]

        # Remove expired routes
        now = datetime.now()
        expired_routes = [
            rid for rid, route in self.routes.items()
            if route.expires_at and now > route.expires_at
        ]
        for rid in expired_routes:
            self.routes[rid].status = RouteStatus.EXPIRED

    def get_statistics(self) -> Dict:
        """Get coordinator statistics."""
        valid_contracts = len([c for c in self.contracts.values() if c.is_valid()])
        active_routes = len([r for r in self.routes.values() 
                           if r.status == RouteStatus.ESTABLISHED])

        return {
            "domains": len(self.domains),
            "contracts": {
                "total": len(self.contracts),
                "valid": valid_contracts,
                "expired": len(self.contracts) - valid_contracts
            },
            "routes": {
                "total": len(self.routes),
                "active": active_routes,
                "by_status": self._count_routes_by_status()
            },
            "topology": {
                "connections": sum(len(neighbors) for neighbors in self.topology.values()) // 2
            }
        }

    def _count_routes_by_status(self) -> Dict[str, int]:
        """Count routes by status."""
        counts = {}
        for route in self.routes.values():
            status = route.status.value
            counts[status] = counts.get(status, 0) + 1
        return counts
