"""Provider API - REST endpoints for cloud providers"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from .provider_manager import ProviderManager

router = APIRouter(prefix="/api/v1/providers", tags=["providers"])
manager = ProviderManager()

class CreateProviderRequest(BaseModel):
    name: str
    provider_type: str
    api_key: str
    base_url: Optional[str] = None

@router.post("/")
async def create_provider(request: CreateProviderRequest):
    """Create a new provider"""
    cred = manager.create_credential(
        name=f"{request.name}-key",
        provider_type=request.provider_type,
        value=request.api_key
    )

    endpoint = {"base_url": request.base_url} if request.base_url else {}
    provider = manager.create_provider(
        name=request.name,
        provider_type=request.provider_type,
        credential_id=cred.credential_id,
        endpoint=endpoint
    )

    return {"status": "success", "provider_id": provider.provider_id}

@router.get("/")
async def list_providers():
    """List providers"""
    providers = manager.list_providers()
    return {"status": "success", "providers": [p.__dict__ for p in providers]}

@router.get("/{provider_id}/models")
async def list_provider_models(provider_id: str):
    """List models from a provider"""
    models = manager.list_external_models(provider_id=provider_id)
    return {"status": "success", "models": [m.__dict__ for m in models]}

def register_api(app):
    """Register provider API routes"""
    app.include_router(router)
