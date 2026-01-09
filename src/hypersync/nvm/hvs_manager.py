"""
HyperSync Hyperbolic Vector Storage (HVS) Manager

Provides schema handling for HVS instances that can be:
- Attached to single models, stacks, or network trunks
- Synchronized across specific dimensions
- Shared between multiple networks for bridging
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field, field_validator
from typing_extensions import Literal

from .block import NVMGeometryConfig, NVMIndexConfig, NVMCodebookConfig


class HVSSyncConfig(BaseModel):
    """Configuration for HVS synchronization across dimensions."""
    enabled: bool = True
    sync_dims: List[int] = Field(default_factory=list, description="Dimension indices to sync")
    sync_mode: Literal["full", "partial", "selective"] = "full"
    sync_interval_ms: Optional[int] = Field(default=None, ge=0)
    conflict_resolution: Literal["last_write_wins", "vector_merge", "manual"] = "last_write_wins"

    @field_validator('sync_dims')
    @classmethod
    def validate_sync_dims(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("sync_dims must contain unique dimension indices")
        if any(d < 0 for d in v):
            raise ValueError("sync_dims must contain non-negative indices")
        return sorted(v)


class HVSAttachmentConfig(BaseModel):
    """Defines what the HVS is attached to."""
    attachment_type: Literal["model", "stack", "trunk", "network", "bridge"]
    attachment_id: str
    attachment_name: Optional[str] = None
    priority: int = Field(default=0, description="Priority for multi-attachment scenarios")


class HVSNetworkBridge(BaseModel):
    """Configuration for bridging multiple networks through shared HVS."""
    bridge_id: str = Field(default_factory=lambda: f"bridge_{uuid.uuid4().hex[:8]}")
    network_ids: List[str] = Field(min_length=2, description="Networks connected by this bridge")
    shared_dims: List[int] = Field(default_factory=list, description="Dimensions shared across networks")
    isolation_policy: Literal["full_share", "read_only", "write_through", "isolated_namespaces"] = "isolated_namespaces"

    @field_validator('network_ids')
    @classmethod
    def validate_network_ids(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("network_ids must be unique")
        return v


class HVSCapacityConfig(BaseModel):
    """Capacity and resource limits for HVS."""
    max_vectors: Optional[int] = Field(default=None, ge=1)
    max_size_mb: Optional[int] = Field(default=None, ge=1)
    vector_dim: int = Field(ge=1)
    growth_policy: Literal["fixed", "auto_expand", "overflow_to_new"] = "auto_expand"


class HVSSchema(BaseModel):
    """Complete schema for a Hyperbolic Vector Storage instance."""

    # Identity
    hvs_id: str = Field(default_factory=lambda: f"hvs_{uuid.uuid4().hex}")
    name: str
    description: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    # Geometry and indexing
    geometry: NVMGeometryConfig
    index: NVMIndexConfig
    codebook: Optional[NVMCodebookConfig] = None

    # Capacity
    capacity: HVSCapacityConfig

    # Attachment
    attachments: List[HVSAttachmentConfig] = Field(default_factory=list)

    # Synchronization
    sync: Optional[HVSSyncConfig] = None

    # Network bridging
    bridges: List[HVSNetworkBridge] = Field(default_factory=list)

    # Metadata
    tags: Dict[str, str] = Field(default_factory=dict)
    tier: Optional[str] = None

    # State
    status: Literal["active", "syncing", "paused", "archived"] = "active"
    vector_count: int = Field(default=0, ge=0)

    model_config = {
        "populate_by_name": True,
        "use_enum_values": True,
    }

    def compute_schema_hash(self) -> str:
        """Compute deterministic hash of schema configuration."""
        payload = self.model_dump(mode="json", exclude={"created_at", "updated_at", "vector_count", "status"})
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return f"sha256:{digest}"

    def is_bridge(self) -> bool:
        """Check if this HVS acts as a network bridge."""
        return len(self.bridges) > 0

    def get_synced_networks(self) -> Set[str]:
        """Get all network IDs connected through bridges."""
        networks = set()
        for bridge in self.bridges:
            networks.update(bridge.network_ids)
        return networks


class HVSManager:
    """Manager for HVS instances."""

    def __init__(self, storage_root: Path):
        self.storage_root = Path(storage_root)
        self.hvs_dir = self.storage_root / "hvs"
        self.hvs_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, HVSSchema] = {}

    def create(self, schema: HVSSchema) -> HVSSchema:
        """Create a new HVS instance."""
        schema.created_at = datetime.utcnow().isoformat()
        schema.updated_at = schema.created_at
        self._save(schema)
        self._cache[schema.hvs_id] = schema
        return schema

    def get(self, hvs_id: str) -> Optional[HVSSchema]:
        """Retrieve an HVS schema by ID."""
        if hvs_id in self._cache:
            return self._cache[hvs_id]

        path = self.hvs_dir / f"{hvs_id}.json"
        if not path.exists():
            raise ValueError(f"HVS not found: {hvs_id}")

        schema = HVSSchema.model_validate_json(path.read_text())
        self._cache[hvs_id] = schema
        return schema

    def update(self, schema: HVSSchema) -> HVSSchema:
        """Update an existing HVS schema."""
        schema.updated_at = datetime.utcnow().isoformat()
        self._save(schema)
        self._cache[schema.hvs_id] = schema
        return schema

    def delete(self, hvs_id: str) -> bool:
        """Delete an HVS instance."""
        path = self.hvs_dir / f"{hvs_id}.json"
        if path.exists():
            path.unlink()
            self._cache.pop(hvs_id, None)
            return True
        return False

    def list_all(self) -> List[HVSSchema]:
        """List all HVS instances."""
        schemas = []
        for path in self.hvs_dir.glob("*.json"):
            try:
                schema = HVSSchema.model_validate_json(path.read_text())
                schemas.append(schema)
                self._cache[schema.hvs_id] = schema
            except Exception:
                continue
        return schemas

    def list_by_attachment(self, attachment_type: str, attachment_id: str) -> List[HVSSchema]:
        """List HVS instances attached to a specific entity."""
        all_hvs = self.list_all()
        return [
            hvs for hvs in all_hvs
            if any(
                att.attachment_type == attachment_type and att.attachment_id == attachment_id
                for att in hvs.attachments
            )
        ]

    def list_bridges(self) -> List[HVSSchema]:
        """List all HVS instances that act as network bridges."""
        return [hvs for hvs in self.list_all() if hvs.is_bridge()]

    def find_bridge_for_networks(self, network_ids: List[str]) -> Optional[HVSSchema]:
        """Find a bridge connecting specific networks."""
        network_set = set(network_ids)
        for hvs in self.list_bridges():
            if network_set.issubset(hvs.get_synced_networks()):
                return hvs
        raise ValueError(f"No bridge found for networks: {network_ids}")

    def _save(self, schema: HVSSchema) -> None:
        """Save schema to disk."""
        path = self.hvs_dir / f"{schema.hvs_id}.json"
        path.write_text(schema.model_dump_json(indent=2))
