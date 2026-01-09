"""
HyperSync Model Catalogue REST API

FastAPI-based REST API for model catalogue operations.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from .model_catalogue_manager import ModelCatalogueManager


app = FastAPI(
    title="HyperSync Model Catalogue API",
    description="REST API for model catalogue management",
    version="1.0.0"
)

# Global manager instance
manager = ModelCatalogueManager()


# Request/Response Models
class ScanRequest(BaseModel):
    path: str
    recursive: bool = True
    auto_tag: bool = True


class ScanResponse(BaseModel):
    model_ids: List[str]
    count: int


class ModelSummary(BaseModel):
    model_id: str
    name: str
    format: str
    size_bytes: int
    added_date: str


class TagRequest(BaseModel):
    tags: List[str]


class NLDProfileRequest(BaseModel):
    nld_level: int = Field(..., ge=0)
    training_domains: List[Dict[str, Any]]
    instability_score: float = Field(..., ge=0, le=1)
    threat_level: str = Field(..., pattern="^(safe|low|medium|high|critical)$")


class TuningSessionRequest(BaseModel):
    parent_model_id: str
    method: str
    dataset_hash: str
    dataset_size: int
    hyperparameters: Dict[str, Any]
    metrics: Dict[str, Any]
    duration_seconds: int
    operator: str
    notes: str = ""


# Endpoints

@app.get("/")
def root():
    """API root."""
    return {
        "name": "HyperSync Model Catalogue API",
        "version": "1.0.0",
        "endpoints": {
            "models": "/models",
            "scan": "/scan",
            "search": "/search",
            "families": "/families",
            "stats": "/stats"
        }
    }


@app.post("/scan", response_model=ScanResponse)
def scan_models(request: ScanRequest):
    """Scan directory or file for models."""
    try:
        from pathlib import Path
        path = Path(request.path)

        if path.is_file():
            model_id = manager.scan_model(str(path), auto_tag=request.auto_tag)
            return ScanResponse(model_ids=[model_id], count=1)

        elif path.is_dir():
            model_ids = manager.scan_directory(str(path), recursive=request.recursive)
            return ScanResponse(model_ids=model_ids, count=len(model_ids))

        else:
            raise HTTPException(status_code=404, detail="Path not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models", response_model=List[ModelSummary])
def list_models(
    format: Optional[str] = Query(None, description="Filter by format"),
    family_id: Optional[str] = Query(None, description="Filter by family"),
    sort_by: str = Query("added_date", description="Sort field"),
    limit: int = Query(100, ge=1, le=1000, description="Max results")
):
    """List models with optional filtering."""
    filter_dict = {}
    if format:
        filter_dict['format'] = format
    if family_id:
        filter_dict['family_id'] = family_id

    models = manager.list_models(filter_dict, sort_by, limit)
    return models


@app.get("/models/{model_id}")
def get_model(model_id: str):
    """Get detailed model information."""
    model = manager.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@app.delete("/models/{model_id}")
def delete_model(model_id: str):
    """Delete model from catalogue."""
    model = manager.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    cursor = manager.conn.cursor()
    cursor.execute("DELETE FROM models WHERE model_id = ?", (model_id,))
    manager.conn.commit()

    return {"status": "deleted", "model_id": model_id}


@app.get("/search")
def search_models(q: str = Query(..., description="Search query")):
    """Search models by name, capability, or tag."""
    results = manager.search_models(q)
    return {"query": q, "results": results, "count": len(results)}


@app.get("/families/{model_id}")
def get_family_tree(model_id: str):
    """Get model family tree."""
    tree = manager.get_family_tree(model_id)
    if not tree:
        raise HTTPException(status_code=404, detail="Model not found")
    return tree


@app.post("/models/{model_id}/tags")
def add_tags(model_id: str, request: TagRequest):
    """Add tags to model."""
    model = manager.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    for tag in request.tags:
        manager.add_tag(model_id, tag)

    return {"status": "added", "tags": request.tags}


@app.delete("/models/{model_id}/tags/{tag}")
def remove_tag(model_id: str, tag: str):
    """Remove tag from model."""
    manager.remove_tag(model_id, tag)
    return {"status": "removed", "tag": tag}


@app.post("/models/{model_id}/nld-profile")
def set_nld_profile(model_id: str, request: NLDProfileRequest):
    """Set nLD profile for model."""
    model = manager.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    manager.set_nld_profile(
        model_id,
        request.nld_level,
        request.training_domains,
        request.instability_score,
        request.threat_level
    )

    return {"status": "updated", "nld_level": request.nld_level}


@app.post("/models/{model_id}/tuning-sessions")
def add_tuning_session(model_id: str, request: TuningSessionRequest):
    """Record a tuning session."""
    session_id = manager.add_tuning_session(
        model_id,
        request.parent_model_id,
        request.method,
        request.dataset_hash,
        request.dataset_size,
        request.hyperparameters,
        request.metrics,
        request.duration_seconds,
        request.operator,
        request.notes
    )

    return {"status": "created", "session_id": session_id}


@app.get("/stats")
def get_stats():
    """Get catalogue statistics."""
    return manager.get_stats()


@app.get("/models/{model_id}/verify")
def verify_model(model_id: str):
    """Verify model file integrity."""
    model = manager.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    import os
    if not os.path.exists(model['path']):
        return {
            "status": "error",
            "message": "File not found",
            "path": model['path']
        }

    current_hash = manager.compute_file_hash(model['path'])
    verified = current_hash == model['content_hash']

    return {
        "status": "verified" if verified else "mismatch",
        "expected_hash": model['content_hash'],
        "current_hash": current_hash,
        "verified": verified
    }


@app.post("/export")
def export_catalogue(output_path: str = "catalogue_export.json"):
    """Export catalogue to JSON."""
    import json

    models = manager.list_models(limit=10000)

    export_data = {
        'exported_at': datetime.utcnow().isoformat() + 'Z',
        'total_models': len(models),
        'models': []
    }

    for model_summary in models:
        model = manager.get_model(model_summary['model_id'])
        export_data['models'].append(model)

    with open(output_path, 'w') as f:
        json.dump(export_data, f, indent=2)

    return {
        "status": "exported",
        "path": output_path,
        "count": len(models)
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    stats = manager.get_stats()
    return {
        "status": "healthy",
        "database": "connected",
        "total_models": stats['total_models']
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# ============================================================================
# DOMAIN INTEGRATION - Added by Pass 2
# ============================================================================

from ..routing.registry import get_registry
from ..routing.domain_factory import get_factory
from ..routing.domain_api import create_api as create_domain_api

# Initialize domain API
_domain_registry = get_registry()
_domain_factory = get_factory()
_domain_api = create_domain_api(_domain_registry, _domain_factory)


def list_geometric_domains(filters=None):
    """List all geometric domains (Lorentzian, pseudo-Riemannian, etc.)"""
    return _domain_api.list_domains(filters)


def get_geometric_domain(domain_id):
    """Get a specific geometric domain"""
    return _domain_api.get_domain(domain_id)


def create_domain_instance(domain_type, parameters, instance_id=None):
    """Create a new domain instance"""
    request = {
        'domain_type': domain_type,
        'parameters': parameters,
        'instance_id': instance_id
    }
    return _domain_api.create_domain_instance(request)


def get_domain_capabilities(domain_id):
    """Get capabilities for a domain"""
    return _domain_api.get_domain_capabilities(domain_id)


def plan_domain_transition(source_domain, target_domain, transition_type='smooth'):
    """Plan a transition between domains"""
    request = {
        'source_domain': source_domain,
        'target_domain': target_domain,
        'transition_type': transition_type
    }
    return _domain_api.plan_transition(request)

