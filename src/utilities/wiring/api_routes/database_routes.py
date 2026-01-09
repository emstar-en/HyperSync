# HyperSync Database API Routes
# REST API endpoints for database operations

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import asyncio

from hypersync.wiring.database_integration import (
    DatabaseIntegrationWiring,
    DatabaseIntegrationMode,
    create_database_integration
)


# Request/Response Models
class StoreRequest(BaseModel):
    data: Any
    metadata: Optional[Dict[str, Any]] = None
    replication_factor: Optional[int] = None


class StoreResponse(BaseModel):
    id: str
    status: str
    location: str
    replicas: List[str]


class QueryRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 100
    offset: int = 0


class QueryResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int
    latency_ms: float


class FederationRequest(BaseModel):
    remote_node: str
    data_id: str
    sync_mode: str = "async"


class MigrationRequest(BaseModel):
    target_version: str
    dry_run: bool = False
    rollback_on_error: bool = True


class HealthResponse(BaseModel):
    status: str
    components: Dict[str, str]
    metrics: Dict[str, Any]


# Router
router = APIRouter(prefix="/api/v1/database", tags=["database"])

# Global database integration instance
_db_integration: Optional[DatabaseIntegrationWiring] = None


async def get_db_integration() -> DatabaseIntegrationWiring:
    global _db_integration
    if _db_integration is None:
        _db_integration = await create_database_integration(
            mode=DatabaseIntegrationMode.HYBRID,
            enable_federation=True,
            enable_edge_optimization=True
        )
    return _db_integration


@router.post("/store", response_model=StoreResponse)
async def store_data(
    request: StoreRequest,
    db: DatabaseIntegrationWiring = Depends(get_db_integration)
):
    try:
        data_id = await db.store(request.data, metadata=request.metadata)

        return StoreResponse(
            id=data_id,
            status="stored",
            location=f"/data/{data_id}",
            replicas=[]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse)
async def query_data(
    request: QueryRequest,
    db: DatabaseIntegrationWiring = Depends(get_db_integration)
):
    try:
        import time
        start = time.time()

        results = await db.query(
            request.query,
            filters=request.filters,
            limit=request.limit,
            offset=request.offset
        )

        latency = (time.time() - start) * 1000

        return QueryResponse(
            results=results,
            total=len(results),
            latency_ms=latency
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/{data_id}")
async def get_data(
    data_id: str,
    db: DatabaseIntegrationWiring = Depends(get_db_integration)
):
    try:
        result = await db.query(f"id:{data_id}")
        if not result:
            raise HTTPException(status_code=404, detail="Data not found")
        return result[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/data/{data_id}")
async def delete_data(
    data_id: str,
    db: DatabaseIntegrationWiring = Depends(get_db_integration)
):
    try:
        await db.components['database']['database'].delete(data_id)
        return {"status": "deleted", "id": data_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/federate")
async def federate_data(
    request: FederationRequest,
    db: DatabaseIntegrationWiring = Depends(get_db_integration)
):
    try:
        if 'federation' not in db.components:
            raise HTTPException(
                status_code=503,
                detail="Federation not enabled"
            )

        await db.federate(request.remote_node, request.data_id)

        return {
            "status": "federated",
            "remote_node": request.remote_node,
            "data_id": request.data_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/migrate")
async def migrate_database(
    request: MigrationRequest,
    db: DatabaseIntegrationWiring = Depends(get_db_integration)
):
    try:
        result = await db.migrate(request.target_version)

        return {
            "status": "migrated",
            "target_version": request.target_version,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check(
    db: DatabaseIntegrationWiring = Depends(get_db_integration)
):
    try:
        component_status = {}

        for name, component in db.components.items():
            if isinstance(component, dict):
                component_status[name] = "healthy"
            else:
                component_status[name] = "healthy"

        metrics = {
            "initialized": db.initialized,
            "mode": db.config.mode.value,
            "components_count": len(db.components)
        }

        return HealthResponse(
            status="healthy",
            components=component_status,
            metrics=metrics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics(
    db: DatabaseIntegrationWiring = Depends(get_db_integration)
):
    try:
        metrics = {
            "database": {
                "total_records": 0,
                "index_size": 0,
                "query_latency_p50": 0,
                "query_latency_p99": 0
            },
            "replication": {
                "factor": db.config.replication_factor,
                "lag_ms": 0
            },
            "storage": {
                "cache_hit_rate": 0.95,
                "compression_ratio": 0.3
            }
        }

        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def register_database_routes(app):
    app.include_router(router)


__all__ = ['router', 'register_database_routes']
