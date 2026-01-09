"""
Tuning Stable API

REST API endpoints for tuning stable management.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from .stable_manager import TuningStableManager

router = APIRouter(prefix="/api/v1/tuning", tags=["tuning"])


# Request/Response Models
class BaseModelRef(BaseModel):
    model_id: str
    catalogue_entry: str
    checkpoint: Optional[str] = None


class TuningConfigModel(BaseModel):
    method: str = "lora"
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    target_modules: List[str] = Field(default_factory=list)
    optimization: Dict[str, Any] = Field(default_factory=dict)


class ValidationConfigModel(BaseModel):
    gold_sample_suite: Optional[str] = None
    validation_frequency: str = "every_epoch"
    quality_gates: Dict[str, Any] = Field(default_factory=dict)
    early_stopping: Dict[str, Any] = Field(default_factory=dict)


class CheckpointConfigModel(BaseModel):
    save_frequency: str = "on_improvement"
    keep_best_n: int = 3
    keep_last_n: int = 2
    auto_catalogue: bool = True


class CICDIntegrationModel(BaseModel):
    pipeline_id: str
    auto_trigger: bool = False
    trigger_on: List[str] = Field(default_factory=list)


class CreateStableRequest(BaseModel):
    name: str
    base_model: BaseModelRef
    description: Optional[str] = None
    tuning_config: Optional[TuningConfigModel] = None
    dataset_config: Optional[Dict] = None
    validation_config: Optional[ValidationConfigModel] = None
    checkpoint_config: Optional[CheckpointConfigModel] = None
    cicd_integration: Optional[CICDIntegrationModel] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict] = None


class StartRunRequest(BaseModel):
    override_config: Optional[Dict] = None


class UpdateProgressRequest(BaseModel):
    progress: Dict
    metrics: Optional[Dict] = None


class SaveCheckpointRequest(BaseModel):
    epoch: int
    step: int
    path: str
    metrics: Dict
    is_best: bool = False
    catalogue_entry: Optional[str] = None


class CompleteRunRequest(BaseModel):
    status: str = "completed"
    error: Optional[Dict] = None


# Initialize manager
manager = TuningStableManager()


@router.post("/stables")
async def create_stable(request: CreateStableRequest):
    """Create a new tuning stable"""
    try:
        stable = manager.create_stable(
            name=request.name,
            base_model=request.base_model.dict(),
            description=request.description,
            tuning_config=request.tuning_config.dict() if request.tuning_config else None,
            dataset_config=request.dataset_config,
            validation_config=request.validation_config.dict() if request.validation_config else None,
            checkpoint_config=request.checkpoint_config.dict() if request.checkpoint_config else None,
            cicd_integration=request.cicd_integration.dict() if request.cicd_integration else None,
            tags=request.tags,
            metadata=request.metadata
        )

        return {
            "status": "success",
            "stable_id": stable.stable_id,
            "stable": stable.__dict__
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stables")
async def list_stables(
    status: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    """List tuning stables"""
    try:
        stables = manager.list_stables(status=status, tags=tags, limit=limit)
        return {
            "status": "success",
            "count": len(stables),
            "stables": [s.__dict__ for s in stables]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stables/{stable_id}")
async def get_stable(stable_id: str):
    """Get a specific stable"""
    stable = manager.get_stable(stable_id)
    if not stable:
        raise HTTPException(status_code=404, detail=f"Stable not found: {stable_id}")

    return {
        "status": "success",
        "stable": stable.__dict__
    }


@router.delete("/stables/{stable_id}")
async def delete_stable(stable_id: str):
    """Delete a stable"""
    stable = manager.get_stable(stable_id)
    if not stable:
        raise HTTPException(status_code=404, detail=f"Stable not found: {stable_id}")

    try:
        manager.delete_stable(stable_id)
        return {
            "status": "success",
            "message": f"Deleted stable: {stable_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/stables/{stable_id}/runs")
async def start_run(stable_id: str, request: StartRunRequest):
    """Start a tuning run"""
    try:
        run = manager.start_run(stable_id, override_config=request.override_config)
        return {
            "status": "success",
            "run_id": run.run_id,
            "run": run.__dict__
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/runs")
async def list_runs(
    stable_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    """List tuning runs"""
    try:
        runs = manager.list_runs(stable_id=stable_id, status=status, limit=limit)
        return {
            "status": "success",
            "count": len(runs),
            "runs": [r.__dict__ for r in runs]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/runs/{run_id}")
async def get_run(run_id: str):
    """Get a specific run"""
    run = manager.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")

    return {
        "status": "success",
        "run": run.__dict__
    }


@router.put("/runs/{run_id}/progress")
async def update_progress(run_id: str, request: UpdateProgressRequest):
    """Update run progress"""
    run = manager.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")

    try:
        manager.update_run_progress(run_id, request.progress, request.metrics)
        return {
            "status": "success",
            "message": "Progress updated"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/runs/{run_id}/checkpoints")
async def save_checkpoint(run_id: str, request: SaveCheckpointRequest):
    """Save a checkpoint"""
    run = manager.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")

    try:
        checkpoint_id = manager.save_checkpoint(
            run_id=run_id,
            stable_id=run.stable_id,
            epoch=request.epoch,
            step=request.step,
            path=request.path,
            metrics=request.metrics,
            is_best=request.is_best,
            catalogue_entry=request.catalogue_entry
        )
        return {
            "status": "success",
            "checkpoint_id": checkpoint_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/runs/{run_id}/complete")
async def complete_run(run_id: str, request: CompleteRunRequest):
    """Complete a run"""
    run = manager.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")

    try:
        manager.complete_run(run_id, status=request.status, error=request.error)
        return {
            "status": "success",
            "message": f"Run completed with status: {request.status}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/checkpoints")
async def list_checkpoints(
    stable_id: Optional[str] = Query(None),
    run_id: Optional[str] = Query(None),
    best_only: bool = Query(False)
):
    """List checkpoints"""
    try:
        checkpoints = manager.get_checkpoints(
            stable_id=stable_id,
            run_id=run_id,
            best_only=best_only
        )
        return {
            "status": "success",
            "count": len(checkpoints),
            "checkpoints": checkpoints
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def register_api(app):
    """Register tuning stable API routes"""
    app.include_router(router)
