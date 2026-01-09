"""
HyperSync HVS API Endpoints

FastAPI endpoints for HVS management accessible to models and users.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..nvm.hvs_manager import (
    HVSManager,
    HVSSchema,
    HVSCapacityConfig,
    HVSAttachmentConfig,
    HVSSyncConfig,
    HVSNetworkBridge,
    NVMGeometryConfig,
    NVMIndexConfig,
    NVMCodebookConfig,
)


# Request/Response models
class CreateHVSRequest(BaseModel):
    name: str
    description: Optional[str] = None
    geometry_space: str = "poincare_ball"
    curvature: Optional[float] = -1.0
    radius_cap: Optional[float] = 0.98
    index_type: str = "hnsw_hyperbolic"
    index_params: dict = Field(default_factory=lambda: {"M": 32, "ef_construction": 200, "ef_runtime": 64})
    vector_dim: int
    max_vectors: Optional[int] = None
    tier: Optional[str] = None


class AttachHVSRequest(BaseModel):
    hvs_id: str
    attachment_type: str
    attachment_id: str
    attachment_name: Optional[str] = None
    priority: int = 0


class ConfigureSyncRequest(BaseModel):
    hvs_id: str
    enabled: bool = True
    sync_dims: List[int] = Field(default_factory=list)
    sync_mode: str = "full"
    conflict_resolution: str = "last_write_wins"


class CreateBridgeRequest(BaseModel):
    hvs_id: str
    network_ids: List[str]
    shared_dims: List[int] = Field(default_factory=list)
    isolation_policy: str = "isolated_namespaces"


class HVSResponse(BaseModel):
    success: bool
    message: str
    hvs: Optional[HVSSchema] = None
    hvs_list: Optional[List[HVSSchema]] = None


# Router
router = APIRouter(prefix="/hvs", tags=["HVS"])

# Global manager (should be initialized with proper storage root)
_manager: Optional[HVSManager] = None


def get_manager() -> HVSManager:
    global _manager
    if _manager is None:
        _manager = HVSManager(Path("./hypersync_data"))
    return _manager


@router.post("/create", response_model=HVSResponse)
async def create_hvs(request: CreateHVSRequest):
    """Create a new HVS instance."""
    try:
        manager = get_manager()

        # Build geometry config
        geom_config = NVMGeometryConfig(
            space=request.geometry_space,
            curvature=request.curvature,
            radius_cap=request.radius_cap
        )

        # Build index config
        index_config = NVMIndexConfig(
            type=request.index_type,
            params=request.index_params
        )

        # Build capacity config
        capacity_config = HVSCapacityConfig(
            vector_dim=request.vector_dim,
            max_vectors=request.max_vectors,
            growth_policy='auto_expand'
        )

        # Build schema
        schema = HVSSchema(
            name=request.name,
            description=request.description,
            geometry=geom_config,
            index=index_config,
            capacity=capacity_config,
            tier=request.tier
        )

        # Create the HVS
        created = manager.create(schema)

        return HVSResponse(
            success=True,
            message=f"Created HVS: {created.name}",
            hvs=created
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list", response_model=HVSResponse)
async def list_hvs(
    attach_type: Optional[str] = Query(None),
    attach_id: Optional[str] = Query(None),
    bridges_only: bool = Query(False)
):
    """List HVS instances with optional filtering."""
    try:
        manager = get_manager()

        if bridges_only:
            hvs_list = manager.list_bridges()
        elif attach_type and attach_id:
            hvs_list = manager.list_by_attachment(attach_type, attach_id)
        else:
            hvs_list = manager.list_all()

        return HVSResponse(
            success=True,
            message=f"Found {len(hvs_list)} HVS instances",
            hvs_list=hvs_list
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/get/{hvs_id}", response_model=HVSResponse)
async def get_hvs(hvs_id: str):
    """Get detailed information about an HVS instance."""
    try:
        manager = get_manager()
        hvs = manager.get(hvs_id)

        if not hvs:
            raise HTTPException(status_code=404, detail=f"HVS not found: {hvs_id}")

        return HVSResponse(
            success=True,
            message=f"Retrieved HVS: {hvs.name}",
            hvs=hvs
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/attach", response_model=HVSResponse)
async def attach_hvs(request: AttachHVSRequest):
    """Attach an HVS to a model, stack, trunk, or network."""
    try:
        manager = get_manager()
        hvs = manager.get(request.hvs_id)

        if not hvs:
            raise HTTPException(status_code=404, detail=f"HVS not found: {request.hvs_id}")

        attachment = HVSAttachmentConfig(
            attachment_type=request.attachment_type,
            attachment_id=request.attachment_id,
            attachment_name=request.attachment_name,
            priority=request.priority
        )

        hvs.attachments.append(attachment)
        updated = manager.update(hvs)

        return HVSResponse(
            success=True,
            message=f"Attached HVS to {request.attachment_type}:{request.attachment_id}",
            hvs=updated
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sync", response_model=HVSResponse)
async def configure_sync(request: ConfigureSyncRequest):
    """Configure synchronization for an HVS instance."""
    try:
        manager = get_manager()
        hvs = manager.get(request.hvs_id)

        if not hvs:
            raise HTTPException(status_code=404, detail=f"HVS not found: {request.hvs_id}")

        sync_config = HVSSyncConfig(
            enabled=request.enabled,
            sync_dims=request.sync_dims,
            sync_mode=request.sync_mode,
            conflict_resolution=request.conflict_resolution
        )

        hvs.sync = sync_config
        updated = manager.update(hvs)

        return HVSResponse(
            success=True,
            message=f"Configured sync for HVS: {hvs.name}",
            hvs=updated
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/bridge", response_model=HVSResponse)
async def create_bridge(request: CreateBridgeRequest):
    """Configure an HVS as a network bridge."""
    try:
        manager = get_manager()
        hvs = manager.get(request.hvs_id)

        if not hvs:
            raise HTTPException(status_code=404, detail=f"HVS not found: {request.hvs_id}")

        bridge = HVSNetworkBridge(
            network_ids=request.network_ids,
            shared_dims=request.shared_dims,
            isolation_policy=request.isolation_policy
        )

        hvs.bridges.append(bridge)
        updated = manager.update(hvs)

        return HVSResponse(
            success=True,
            message=f"Created bridge in HVS: {hvs.name}",
            hvs=updated
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/delete/{hvs_id}", response_model=HVSResponse)
async def delete_hvs(hvs_id: str):
    """Delete an HVS instance."""
    try:
        manager = get_manager()

        if manager.delete(hvs_id):
            return HVSResponse(
                success=True,
                message=f"Deleted HVS: {hvs_id}"
            )
        else:
            raise HTTPException(status_code=404, detail=f"HVS not found: {hvs_id}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/bridges/find")
async def find_bridge(network_ids: str = Query(..., description="Comma-separated network IDs")):
    """Find a bridge connecting specific networks."""
    try:
        manager = get_manager()
        net_list = [n.strip() for n in network_ids.split(',')]

        bridge = manager.find_bridge_for_networks(net_list)

        if bridge:
            return HVSResponse(
                success=True,
                message=f"Found bridge: {bridge.name}",
                hvs=bridge
            )
        else:
            return HVSResponse(
                success=False,
                message="No bridge found for specified networks"
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
