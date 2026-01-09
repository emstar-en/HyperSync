"""
Assembly API

REST API endpoints for model stacks and node assemblies.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from .assembly_manager import AssemblyManager

router = APIRouter(prefix="/api/v1/assembly", tags=["assembly"])
manager = AssemblyManager()


# Request/Response Models
class ModelInStack(BaseModel):
    role: str
    model_id: str
    catalogue_entry: Optional[str] = None
    checkpoint: Optional[str] = None
    config: Optional[Dict] = None
    priority: int = 10
    fallback: Optional[str] = None


class CreateStackRequest(BaseModel):
    name: str
    models: List[ModelInStack]
    description: Optional[str] = None
    orchestration: Optional[Dict] = None
    resource_requirements: Optional[Dict] = None
    nvm_assignments: Optional[List[Dict]] = None
    capabilities: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict] = None


class CreateAssemblyRequest(BaseModel):
    name: str
    stack_id: str
    target_ld: str
    description: Optional[str] = None
    security_level: str = "secure"
    network_config: Optional[Dict] = None
    security_config: Optional[Dict] = None
    monitoring_config: Optional[Dict] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict] = None


# Stack Endpoints
@router.post("/stacks")
async def create_stack(request: CreateStackRequest):
    """Create a new model stack"""
    try:
        stack = manager.create_stack(
            name=request.name,
            models=[m.dict() for m in request.models],
            description=request.description,
            orchestration=request.orchestration,
            resource_requirements=request.resource_requirements,
            nvm_assignments=request.nvm_assignments,
            capabilities=request.capabilities,
            tags=request.tags,
            metadata=request.metadata
        )
        return {"status": "success", "stack_id": stack.stack_id, "stack": stack.__dict__}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stacks")
async def list_stacks(
    tags: Optional[List[str]] = Query(None),
    capabilities: Optional[List[str]] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    """List model stacks"""
    stacks = manager.list_stacks(tags=tags, capabilities=capabilities, limit=limit)
    return {"status": "success", "count": len(stacks), "stacks": [s.__dict__ for s in stacks]}


@router.get("/stacks/{stack_id}")
async def get_stack(stack_id: str):
    """Get a specific stack"""
    stack = manager.get_stack(stack_id)
    if not stack:
        raise HTTPException(status_code=404, detail=f"Stack not found: {stack_id}")
    return {"status": "success", "stack": stack.__dict__}


@router.delete("/stacks/{stack_id}")
async def delete_stack(stack_id: str):
    """Delete a stack"""
    try:
        manager.delete_stack(stack_id)
        return {"status": "success", "message": f"Deleted stack: {stack_id}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Assembly Endpoints
@router.post("/assemblies")
async def create_assembly(request: CreateAssemblyRequest):
    """Create a new node assembly"""
    try:
        assembly = manager.create_assembly(
            name=request.name,
            stack_id=request.stack_id,
            target_ld=request.target_ld,
            description=request.description,
            security_level=request.security_level,
            network_config=request.network_config,
            security_config=request.security_config,
            monitoring_config=request.monitoring_config,
            tags=request.tags,
            metadata=request.metadata
        )
        return {"status": "success", "assembly_id": assembly.assembly_id, "assembly": assembly.__dict__}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/assemblies")
async def list_assemblies(
    stack_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    """List node assemblies"""
    assemblies = manager.list_assemblies(stack_id=stack_id, status=status, limit=limit)
    return {"status": "success", "count": len(assemblies), "assemblies": [a.__dict__ for a in assemblies]}


@router.get("/assemblies/{assembly_id}")
async def get_assembly(assembly_id: str):
    """Get a specific assembly"""
    assembly = manager.get_assembly(assembly_id)
    if not assembly:
        raise HTTPException(status_code=404, detail=f"Assembly not found: {assembly_id}")
    return {"status": "success", "assembly": assembly.__dict__}


@router.post("/assemblies/{assembly_id}/validate")
async def validate_assembly(assembly_id: str):
    """Validate an assembly"""
    try:
        results = manager.validate_assembly(assembly_id)
        return {"status": "success", "validation": results}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/assemblies/{assembly_id}/deploy")
async def deploy_assembly(assembly_id: str):
    """Deploy an assembly"""
    try:
        deployment = manager.deploy_assembly(assembly_id)
        return {"status": "success", "deployment_id": deployment.deployment_id, "deployment": deployment.__dict__}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/deployments")
async def list_deployments(
    assembly_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    """List deployments"""
    deployments = manager.list_deployments(assembly_id=assembly_id, status=status, limit=limit)
    return {"status": "success", "count": len(deployments), "deployments": [d.__dict__ for d in deployments]}


@router.get("/deployments/{deployment_id}")
async def get_deployment(deployment_id: str):
    """Get a specific deployment"""
    deployment = manager.get_deployment(deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail=f"Deployment not found: {deployment_id}")
    return {"status": "success", "deployment": deployment.__dict__}


@router.post("/deployments/{deployment_id}/stop")
async def stop_deployment(deployment_id: str):
    """Stop a deployment"""
    try:
        manager.stop_deployment(deployment_id)
        return {"status": "success", "message": f"Stopped deployment: {deployment_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def register_api(app):
    """Register assembly API routes"""
    app.include_router(router)
