"""
Base bridge interface for external orchestrator integration.

Provides common interface for Kubernetes, Nomad, Airflow, and other orchestrators.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class BridgeType(str, Enum):
    """Supported orchestrator types."""
    KUBERNETES = "kubernetes"
    NOMAD = "nomad"
    AIRFLOW = "airflow"
    CUSTOM = "custom"


class BridgeStatus(str, Enum):
    """Bridge connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    INITIALIZING = "initializing"


@dataclass
class BridgeConfig:
    """Bridge configuration."""
    bridge_type: BridgeType
    name: str
    endpoint: str
    credentials: Dict[str, Any] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class WorkloadMapping:
    """Mapping between external and HyperSync workloads."""
    external_id: str
    external_type: str
    hypersync_id: str
    hypersync_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PlacementAdvice:
    """Placement advice from HyperSync to external orchestrator."""
    workload_id: str
    recommended_node: str
    coordinates: List[float]
    distance: float
    confidence: float
    reasoning: str
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BridgeReceipt:
    """Receipt for bridge operations."""
    receipt_id: str
    bridge_type: BridgeType
    operation: str
    workload_id: str
    status: str
    placement_advice: Optional[PlacementAdvice] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "receipt_id": self.receipt_id,
            "bridge_type": self.bridge_type.value,
            "operation": self.operation,
            "workload_id": self.workload_id,
            "status": self.status,
            "placement_advice": self._placement_to_dict() if self.placement_advice else None,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }

    def _placement_to_dict(self) -> Dict[str, Any]:
        """Convert placement advice to dict."""
        if not self.placement_advice:
            return None

        return {
            "workload_id": self.placement_advice.workload_id,
            "recommended_node": self.placement_advice.recommended_node,
            "coordinates": self.placement_advice.coordinates,
            "distance": self.placement_advice.distance,
            "confidence": self.placement_advice.confidence,
            "reasoning": self.placement_advice.reasoning,
            "alternatives": self.placement_advice.alternatives,
            "timestamp": self.placement_advice.timestamp.isoformat()
        }


class OrchestratorBridge(ABC):
    """
    Abstract base class for orchestrator bridges.

    Bridges connect HyperSync to external orchestrators, enabling:
    - Placement advice queries
    - Workload synchronization
    - Receipt generation
    - Bidirectional state sync
    """

    def __init__(self, config: BridgeConfig):
        self.config = config
        self.status = BridgeStatus.INITIALIZING
        self.workload_mappings: Dict[str, WorkloadMapping] = {}
        self.receipts: List[BridgeReceipt] = []

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to external orchestrator.

        Returns:
            True if connection successful
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from external orchestrator.

        Returns:
            True if disconnection successful
        """
        pass

    @abstractmethod
    def get_workloads(self) -> List[Dict[str, Any]]:
        """
        Get all workloads from external orchestrator.

        Returns:
            List of workload specifications
        """
        pass

    @abstractmethod
    def get_workload(self, workload_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific workload from external orchestrator.

        Args:
            workload_id: External workload identifier

        Returns:
            Workload specification or None
        """
        pass

    @abstractmethod
    def provide_placement_advice(self, workload_spec: Dict[str, Any]) -> PlacementAdvice:
        """
        Provide placement advice for workload.

        Args:
            workload_spec: Workload specification from external orchestrator

        Returns:
            Placement advice from HyperSync
        """
        pass

    @abstractmethod
    def sync_workload_state(self, workload_id: str, state: Dict[str, Any]) -> bool:
        """
        Sync workload state to external orchestrator.

        Args:
            workload_id: Workload identifier
            state: State to sync

        Returns:
            True if sync successful
        """
        pass

    def register_workload_mapping(self, mapping: WorkloadMapping):
        """Register mapping between external and HyperSync workload."""
        self.workload_mappings[mapping.external_id] = mapping

    def get_workload_mapping(self, external_id: str) -> Optional[WorkloadMapping]:
        """Get workload mapping by external ID."""
        return self.workload_mappings.get(external_id)

    def generate_receipt(self, operation: str, workload_id: str, 
                        status: str, placement_advice: Optional[PlacementAdvice] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> BridgeReceipt:
        """Generate receipt for bridge operation."""
        receipt_id = f"br_{self.config.bridge_type.value}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        receipt = BridgeReceipt(
            receipt_id=receipt_id,
            bridge_type=self.config.bridge_type,
            operation=operation,
            workload_id=workload_id,
            status=status,
            placement_advice=placement_advice,
            metadata=metadata or {}
        )

        self.receipts.append(receipt)
        return receipt

    def get_receipts(self, workload_id: Optional[str] = None) -> List[BridgeReceipt]:
        """Get receipts, optionally filtered by workload ID."""
        if workload_id:
            return [r for r in self.receipts if r.workload_id == workload_id]
        return self.receipts

    def health_check(self) -> Dict[str, Any]:
        """Check bridge health."""
        return {
            "bridge_type": self.config.bridge_type.value,
            "name": self.config.name,
            "status": self.status.value,
            "endpoint": self.config.endpoint,
            "workload_count": len(self.workload_mappings),
            "receipt_count": len(self.receipts)
        }
