"""
HyperSync CI/CD REST API

FastAPI-based REST API for CI/CD pipeline management.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from .pipeline_manager import PipelineManager
from .gold_sample_manager import GoldSampleManager
from .pipeline_executor import PipelineExecutor

app = FastAPI(title="HyperSync CI/CD API", version="1.0.0")

# Initialize managers
pipeline_manager = PipelineManager()
gold_sample_manager = GoldSampleManager()
pipeline_executor = PipelineExecutor(pipeline_manager, gold_sample_manager)


# Models
class PipelineCreate(BaseModel):
    definition: Dict[str, Any]


class PipelineRun(BaseModel):
    pipeline_id: str
    trigger_type: str = "api"
    trigger_source: str = "api_user"


class GoldSampleCreate(BaseModel):
    pipeline_id: str
    stage: str
    data: Dict[str, Any]
    step: Optional[str] = None
    version: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class GoldSampleValidate(BaseModel):
    sample_id: str
    test_data: Dict[str, Any]
    comparison_method: str = "fuzzy"
    threshold: float = 0.95


# Pipeline Endpoints
@app.post("/api/v1/pipelines")
def create_pipeline(pipeline: PipelineCreate):
    """Create a new pipeline"""
    try:
        pipeline_id = pipeline_manager.create_pipeline(pipeline.definition)
        return {"pipeline_id": pipeline_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/pipelines")
def list_pipelines(active_only: bool = True):
    """List all pipelines"""
    pipelines = pipeline_manager.list_pipelines(active_only)
    return {"pipelines": pipelines, "count": len(pipelines)}


@app.get("/api/v1/pipelines/{pipeline_id}")
def get_pipeline(pipeline_id: str):
    """Get pipeline details"""
    pipeline = pipeline_manager.get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return pipeline


@app.delete("/api/v1/pipelines/{pipeline_id}")
def delete_pipeline(pipeline_id: str):
    """Delete a pipeline"""
    try:
        pipeline_manager.delete_pipeline(pipeline_id)
        return {"status": "deleted", "pipeline_id": pipeline_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Run Endpoints
@app.post("/api/v1/runs")
def start_run(run_request: PipelineRun, background_tasks: BackgroundTasks):
    """Start a pipeline run"""
    try:
        # Execute in background
        run_id = pipeline_manager.start_run(
            run_request.pipeline_id,
            run_request.trigger_type,
            run_request.trigger_source
        )

        background_tasks.add_task(
            pipeline_executor.execute_pipeline,
            run_request.pipeline_id,
            run_request.trigger_type,
            run_request.trigger_source
        )

        return {"run_id": run_id, "status": "started"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/runs")
def list_runs(pipeline_id: Optional[str] = None, limit: int = 50):
    """List pipeline runs"""
    runs = pipeline_manager.list_runs(pipeline_id, limit)
    return {"runs": runs, "count": len(runs)}


@app.get("/api/v1/runs/{run_id}")
def get_run(run_id: str):
    """Get run details"""
    run = pipeline_manager.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.get("/api/v1/runs/{run_id}/artifacts")
def get_run_artifacts(run_id: str):
    """Get artifacts for a run"""
    artifacts = pipeline_manager.get_artifacts(run_id)
    return {"artifacts": artifacts, "count": len(artifacts)}


# Gold Sample Endpoints
@app.post("/api/v1/gold-samples")
def create_gold_sample(sample: GoldSampleCreate):
    """Create a new gold sample"""
    try:
        sample_id = gold_sample_manager.create_sample(
            sample.pipeline_id,
            sample.stage,
            sample.data,
            step=sample.step,
            version=sample.version,
            metadata=sample.metadata
        )
        return {"sample_id": sample_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/gold-samples")
def list_gold_samples(
    pipeline_id: Optional[str] = None,
    stage: Optional[str] = None,
    version: Optional[str] = None
):
    """List gold samples"""
    samples = gold_sample_manager.list_samples(pipeline_id, stage, version)
    return {"samples": samples, "count": len(samples)}


@app.get("/api/v1/gold-samples/{sample_id}")
def get_gold_sample(sample_id: str):
    """Get gold sample details"""
    sample = gold_sample_manager.get_sample(sample_id)
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample


@app.post("/api/v1/gold-samples/validate")
def validate_gold_sample(validation: GoldSampleValidate):
    """Validate test data against a gold sample"""
    try:
        passed, score, differences = gold_sample_manager.validate_against_sample(
            validation.sample_id,
            validation.test_data,
            comparison_method=validation.comparison_method,
            threshold=validation.threshold
        )

        return {
            "passed": passed,
            "similarity_score": score,
            "differences": differences,
            "threshold": validation.threshold
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/gold-samples/{sample_id}/history")
def get_validation_history(sample_id: str):
    """Get validation history for a gold sample"""
    history = gold_sample_manager.get_validation_history(sample_id)
    return {"history": history, "count": len(history)}


@app.delete("/api/v1/gold-samples/{sample_id}")
def deactivate_gold_sample(sample_id: str):
    """Deactivate a gold sample"""
    try:
        gold_sample_manager.deactivate_sample(sample_id)
        return {"status": "deactivated", "sample_id": sample_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Health Check
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "hypersync-cicd-api"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
