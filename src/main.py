from fastapi import FastAPI
from api.routers import geometry, consensus
from core.registry import registry
from core.geometry import default_geometry # Triggers registration
from agents.ux_orchestrator import create_orchestrator
from core.consensus import default_consensus # Triggers registration
from core.processors import default_ustab_processor # Triggers registration
from subsystems.audio.engine import default_audio # Triggers registration
from core.routing.router import default_router # Triggers registration

app = FastAPI(
    title="HyperSync Core",
    description="Geometry-Aware Orchestration System with Native Extensibility",
    version="0.1.0"
)

# Include Routers
app.include_router(geometry.router, prefix="/geometry", tags=["Geometry"])
app.include_router(consensus.router, prefix="/consensus", tags=["Consensus"])


# Initialize UX Orchestrator
ux_orchestrator = create_orchestrator()

@app.get("/")
async def root():
    return {"message": "HyperSync Core Online", "status": "active"}

@app.get("/system/introspect")
async def introspect():
    """
    Returns the current system lattice for Agent consumption.
    """
    return registry.introspect()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.post("/ux/ask")
async def ask_ux_orchestrator(query: str):
    """
    Direct channel to the UX Orchestrator.
    """
    response = ux_orchestrator.process_request(query)
    return {"response": response}
