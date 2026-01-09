"""
HyperSync NVM API

REST API endpoints for NVM block management with hyperbolic embedding,
assignments, directory management, and preloading capabilities.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import os

from .nvm_schema_manager import (
    NVMSchemaManager,
    NVMBlockClass,
    NVMAssignmentType,
    NVMAccessMode,
    NVMGeometryConfig,
    NVMIndexConfig,
    NVMCodebookConfig,
)


# Pydantic models for API

class GeometryConfigRequest(BaseModel):
    space: str = Field(default="poincare_ball", description="Geometry space")
    curvature: float = Field(default=-1.0, description="Curvature")
    radius_cap: float = Field(default=0.98, description="Radius cap")
    dimension: int = Field(default=768, description="Vector dimension")
    metric: str = Field(default="poincare", description="Distance metric")
    transport: str = Field(default="parallel", description="Transport method")


class IndexConfigRequest(BaseModel):
    index_type: str = Field(default="hnsw_hyperbolic", description="Index type")
    ef_construction: int = Field(default=200, description="EF construction")
    ef_search: int = Field(default=100, description="EF search")
    m_neighbors: int = Field(default=32, description="M neighbors")
    quantization: Optional[str] = Field(default="opq", description="Quantization method")


class CodebookConfigRequest(BaseModel):
    method: str = Field(default="opq", description="Codebook method")
    n_subvectors: int = Field(default=8, description="Number of subvectors")
    bits_per_code: int = Field(default=8, description="Bits per code")
    training_size: int = Field(default=10000, description="Training size")


class CreateBlockRequest(BaseModel):
    block_id: str = Field(..., description="Unique block identifier")
    name: str = Field(..., description="Block name")
    description: str = Field(..., description="Block description")
    block_class: str = Field(default="documentation", description="Block class")
    geometry: Optional[GeometryConfigRequest] = None
    index: Optional[IndexConfigRequest] = None
    codebook: Optional[CodebookConfigRequest] = None
    max_vectors: Optional[int] = None
    max_size_mb: Optional[int] = None
    retention_days: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AssignBlockRequest(BaseModel):
    block_id: str = Field(..., description="Block identifier")
    assignment_type: str = Field(..., description="Assignment type")
    target_id: str = Field(..., description="Target entity ID")
    target_name: Optional[str] = None
    access_mode: str = Field(default="read_write", description="Access mode")
    priority: int = Field(default=0, description="Priority")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AddDirectoryRequest(BaseModel):
    block_id: str = Field(..., description="Block identifier")
    directory_id: str = Field(..., description="Directory identifier")
    path: str = Field(..., description="Directory path")
    purpose: str = Field(..., description="Directory purpose")
    max_size_mb: Optional[int] = None
    allowed_extensions: List[str] = Field(default_factory=list)
    auto_embed: bool = Field(default=True)
    watch_changes: bool = Field(default=False)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AddPreloadRequest(BaseModel):
    block_id: str = Field(..., description="Block identifier")
    preload_id: str = Field(..., description="Preload identifier")
    source_type: str = Field(..., description="Source type")
    source_path: Optional[str] = None
    content: Optional[str] = None
    content_type: str = Field(default="text/markdown")
    chunk_size: int = Field(default=512)
    overlap: int = Field(default=50)
    auto_embed: bool = Field(default=True)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CreatePresetRequest(BaseModel):
    preset: str = Field(..., description="Preset name")
    target_id: str = Field(..., description="Target entity ID")
    target_name: Optional[str] = None


# API Router

def create_nvm_api(storage_path: Optional[Path] = None) -> FastAPI:
    """Create NVM API application"""

    app = FastAPI(
        title="HyperSync NVM API",
        description="API for managing NVM blocks with hyperbolic embedding",
        version="2.0.0"
    )

    if storage_path is None:
        storage_path = Path(os.environ.get('NVM_STORAGE_PATH', './nvm_storage'))

    manager = NVMSchemaManager(storage_path)

    @app.post("/nvm/blocks", tags=["blocks"])
    async def create_block(request: CreateBlockRequest) -> Dict[str, Any]:
        """Create a new NVM block"""

        try:
            geometry = None
            if request.geometry:
                geometry = NVMGeometryConfig(**request.geometry.dict())

            index = None
            if request.index:
                index = NVMIndexConfig(**request.index.dict())

            codebook = None
            if request.codebook:
                codebook = NVMCodebookConfig(**request.codebook.dict())

            block = manager.create_block(
                block_id=request.block_id,
                name=request.name,
                description=request.description,
                block_class=NVMBlockClass(request.block_class),
                geometry=geometry,
                index=index,
                codebook=codebook,
                max_vectors=request.max_vectors,
                max_size_mb=request.max_size_mb,
                retention_days=request.retention_days,
                metadata=request.metadata
            )

            return {
                "status": "success",
                "block": block.to_dict()
            }

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/nvm/assignments", tags=["assignments"])
    async def assign_block(request: AssignBlockRequest) -> Dict[str, Any]:
        """Assign NVM block to entity"""

        try:
            assignment = manager.assign_block(
                block_id=request.block_id,
                assignment_type=NVMAssignmentType(request.assignment_type),
                target_id=request.target_id,
                target_name=request.target_name,
                access_mode=NVMAccessMode(request.access_mode),
                priority=request.priority,
                metadata=request.metadata
            )

            return {
                "status": "success",
                "assignment": assignment.to_dict()
            }

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/nvm/directories", tags=["directories"])
    async def add_directory(request: AddDirectoryRequest) -> Dict[str, Any]:
        """Add directory to NVM block"""

        try:
            directory = manager.add_directory(
                block_id=request.block_id,
                directory_id=request.directory_id,
                path=request.path,
                purpose=request.purpose,
                max_size_mb=request.max_size_mb,
                allowed_extensions=request.allowed_extensions,
                auto_embed=request.auto_embed,
                watch_changes=request.watch_changes,
                metadata=request.metadata
            )

            return {
                "status": "success",
                "directory": directory.to_dict()
            }

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/nvm/preloads", tags=["preloads"])
    async def add_preload(request: AddPreloadRequest) -> Dict[str, Any]:
        """Add preload configuration to NVM block"""

        try:
            preload = manager.add_preload(
                block_id=request.block_id,
                preload_id=request.preload_id,
                source_type=request.source_type,
                source_path=request.source_path,
                content=request.content,
                content_type=request.content_type,
                chunk_size=request.chunk_size,
                overlap=request.overlap,
                auto_embed=request.auto_embed,
                metadata=request.metadata
            )

            return {
                "status": "success",
                "preload": preload.to_dict()
            }

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/nvm/blocks", tags=["blocks"])
    async def list_blocks(
        block_class: Optional[str] = Query(None, description="Filter by block class"),
        assignment_type: Optional[str] = Query(None, description="Filter by assignment type"),
        target_id: Optional[str] = Query(None, description="Filter by target ID")
    ) -> Dict[str, Any]:
        """List NVM blocks with optional filtering"""

        try:
            blocks = manager.list_blocks(
                block_class=NVMBlockClass(block_class) if block_class else None,
                assignment_type=NVMAssignmentType(assignment_type) if assignment_type else None,
                target_id=target_id
            )

            return {
                "status": "success",
                "count": len(blocks),
                "blocks": [block.to_dict() for block in blocks]
            }

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/nvm/blocks/{block_id}", tags=["blocks"])
    async def get_block(block_id: str) -> Dict[str, Any]:
        """Get NVM block details"""

        try:
            block = manager.get_block(block_id)

            if not block:
                raise HTTPException(status_code=404, detail=f"Block not found: {block_id}")

            return {
                "status": "success",
                "block": block.to_dict()
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.delete("/nvm/blocks/{block_id}", tags=["blocks"])
    async def delete_block(block_id: str) -> Dict[str, Any]:
        """Delete NVM block"""

        try:
            success = manager.delete_block(block_id)

            if not success:
                raise HTTPException(status_code=404, detail=f"Block not found: {block_id}")

            return {
                "status": "success",
                "message": f"Block deleted: {block_id}"
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/nvm/presets", tags=["presets"])
    async def create_preset(request: CreatePresetRequest) -> Dict[str, Any]:
        """Create NVM block from preset"""

        presets = {
            'hypersync_docs': {
                'block_id': f'nvm://docs/hypersync/{request.target_id.split("/")[-1]}',
                'name': 'HyperSync Documentation',
                'description': 'Preloaded HyperSync documentation for assistant model',
                'block_class': NVMBlockClass.DOCUMENTATION,
                'preloads': [
                    {
                        'preload_id': 'hypersync_readme',
                        'source_type': 'directory',
                        'source_path': './docs',
                        'content_type': 'text/markdown'
                    }
                ]
            },
            'model_cache': {
                'block_id': f'nvm://cache/{request.target_id.split("/")[-1]}',
                'name': 'Model Cache',
                'description': 'Hyperbolic cache for model computations',
                'block_class': NVMBlockClass.CACHE,
                'max_vectors': 100000,
                'retention_days': 7
            },
            'training_data': {
                'block_id': f'nvm://training/{request.target_id.split("/")[-1]}',
                'name': 'Training Data',
                'description': 'Training data with hyperbolic embeddings',
                'block_class': NVMBlockClass.TRAINING_DATA,
                'max_size_mb': 10240
            },
            'logs': {
                'block_id': f'nvm://logs/{request.target_id.split("/")[-1]}',
                'name': 'Operation Logs',
                'description': 'Operational logs and telemetry',
                'block_class': NVMBlockClass.LOGS,
                'retention_days': 30
            }
        }

        if request.preset not in presets:
            raise HTTPException(status_code=400, detail=f"Unknown preset: {request.preset}")

        try:
            config = presets[request.preset]

            # Create block
            block = manager.create_block(
                block_id=config['block_id'],
                name=config['name'],
                description=config['description'],
                block_class=config['block_class'],
                max_vectors=config.get('max_vectors'),
                max_size_mb=config.get('max_size_mb'),
                retention_days=config.get('retention_days')
            )

            # Assign to target
            assignment = manager.assign_block(
                block_id=config['block_id'],
                assignment_type=NVMAssignmentType.MODEL,
                target_id=request.target_id,
                target_name=request.target_name,
                access_mode=NVMAccessMode.READ_WRITE
            )

            # Add preloads if specified
            preloads = []
            for preload_config in config.get('preloads', []):
                preload = manager.add_preload(
                    block_id=config['block_id'],
                    **preload_config
                )
                preloads.append(preload.to_dict())

            return {
                "status": "success",
                "preset": request.preset,
                "block": block.to_dict(),
                "assignment": assignment.to_dict(),
                "preloads": preloads
            }

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/nvm/health", tags=["system"])
    async def health_check() -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "nvm-api",
            "version": "2.0.0"
        }

    return app


# For running standalone
if __name__ == "__main__":
    import uvicorn

    app = create_nvm_api()
    uvicorn.run(app, host="0.0.0.0", port=8000)
