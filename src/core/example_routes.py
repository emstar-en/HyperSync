"""
Example Route Module - Template for creating route modules.

This shows how to structure a route module for auto-discovery.
"""
import logging
from typing import List, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel

from hypersync.api.router_registry import (
    APIRouterRegistry,
    RouteCategory,
    HTTPMethod
)

logger = logging.getLogger(__name__)


# Request/Response Models
class MeshNodeResponse(BaseModel):
    """Mesh node response model."""
    node_id: str
    status: str
    address: str
    last_seen: str


class MeshListResponse(BaseModel):
    """Mesh list response model."""
    nodes: List[MeshNodeResponse]
    total: int


class MeshStatusResponse(BaseModel):
    """Mesh status response model."""
    total_nodes: int
    active_nodes: int
    inactive_nodes: int
    health_percentage: float


def register_routes(registry: APIRouterRegistry):
    """
    Register mesh routes with the API registry.

    This function is called by the route loader.

    Args:
        registry: The API router registry instance
    """

    # Register mesh router group
    registry.register_group(
        name="mesh",
        prefix="/api/v1/mesh",
        category=RouteCategory.MESH
    )

    # Register mesh:list route
    registry.register_route(
        group_name="mesh",
        path="/nodes",
        method=HTTPMethod.GET,
        handler=get_mesh_nodes,
        summary="List mesh nodes",
        description="Get a list of all mesh nodes in the network",
        tags=["mesh"],
        response_model=MeshListResponse
    )

    # Register mesh:status route
    registry.register_route(
        group_name="mesh",
        path="/status",
        method=HTTPMethod.GET,
        handler=get_mesh_status,
        summary="Get mesh status",
        description="Get overall mesh network status",
        tags=["mesh"],
        response_model=MeshStatusResponse
    )

    # Register mesh:node route
    registry.register_route(
        group_name="mesh",
        path="/nodes/{node_id}",
        method=HTTPMethod.GET,
        handler=get_mesh_node,
        summary="Get mesh node",
        description="Get details for a specific mesh node",
        tags=["mesh"],
        response_model=MeshNodeResponse
    )


async def get_mesh_nodes(
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> MeshListResponse:
    """
    Get list of mesh nodes.

    Args:
        status: Filter by status (active, inactive)
        limit: Maximum number of nodes to return
        offset: Offset for pagination

    Returns:
        List of mesh nodes
    """
    logger.info(f"Getting mesh nodes (status={status}, limit={limit}, offset={offset})")

    # TODO: Implement actual mesh node retrieval
    nodes = [
        MeshNodeResponse(
            node_id="node-1",
            status="active",
            address="10.0.0.1:8080",
            last_seen="2025-11-20T12:00:00Z"
        ),
        MeshNodeResponse(
            node_id="node-2",
            status="active",
            address="10.0.0.2:8080",
            last_seen="2025-11-20T12:00:00Z"
        ),
        MeshNodeResponse(
            node_id="node-3",
            status="inactive",
            address="10.0.0.3:8080",
            last_seen="2025-11-19T12:00:00Z"
        )
    ]

    # Filter by status if provided
    if status:
        nodes = [n for n in nodes if n.status == status]

    # Apply pagination
    paginated_nodes = nodes[offset:offset + limit]

    return MeshListResponse(
        nodes=paginated_nodes,
        total=len(nodes)
    )


async def get_mesh_status() -> MeshStatusResponse:
    """
    Get mesh network status.

    Returns:
        Mesh network status
    """
    logger.info("Getting mesh network status")

    # TODO: Implement actual mesh status retrieval
    return MeshStatusResponse(
        total_nodes=3,
        active_nodes=2,
        inactive_nodes=1,
        health_percentage=85.0
    )


async def get_mesh_node(node_id: str) -> MeshNodeResponse:
    """
    Get specific mesh node.

    Args:
        node_id: Node ID

    Returns:
        Mesh node details

    Raises:
        HTTPException: If node not found
    """
    logger.info(f"Getting mesh node: {node_id}")

    # TODO: Implement actual mesh node retrieval
    if node_id == "node-1":
        return MeshNodeResponse(
            node_id="node-1",
            status="active",
            address="10.0.0.1:8080",
            last_seen="2025-11-20T12:00:00Z"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {node_id} not found"
        )
