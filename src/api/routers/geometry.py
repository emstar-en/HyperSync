from fastapi import APIRouter, HTTPException, Body
from typing import Dict, List
from ..models import SectorState, AgentPosition, PolarCoordinate, Point

router = APIRouter(
    prefix="/geometry",
    tags=["geometry"]
)

# In-memory mock store
_geometry_store = {
    "sectors": {
        "sector_01": {
            "sector_id": "sector_01",
            "coordinator_id": "coord_alpha",
            "boundary_points": [{"x": 0.1, "y": 0.1}, {"x": 0.5, "y": 0.5}],
            "worker_count": 12,
            "density": 0.42
        }
    },
    "agents": {
        "agent_007": {
            "agent_id": "agent_007",
            "position": {"r": 0.3, "theta": 1.57},
            "drift_vector": 0.015,
            "status": "active"
        }
    }
}

@router.get("/sector/{sector_id}", response_model=SectorState)
async def get_sector_state(sector_id: str):
    """
    Retrieve the current geometric state of a specific Voronoi sector.
    """
    sector = _geometry_store["sectors"].get(sector_id)
    if not sector:
        # Return a default mock if not found, for ease of testing
        return SectorState(
            sector_id=sector_id,
            coordinator_id="unknown",
            boundary_points=[],
            worker_count=0,
            density=0.0
        )
    return sector

@router.get("/agent/{agent_id}", response_model=AgentPosition)
async def get_agent_position(agent_id: str):
    """
    Retrieve the current Poincaré coordinates and drift status of an agent.
    """
    agent = _geometry_store["agents"].get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.post("/agent/{agent_id}/move")
async def update_agent_position(agent_id: str, position: PolarCoordinate):
    """
    Update an agent's position (Simulation/Test hook).
    """
    if agent_id not in _geometry_store["agents"]:
        _geometry_store["agents"][agent_id] = {
            "agent_id": agent_id,
            "position": position.dict(),
            "drift_vector": 0.0,
            "status": "active"
        }
    else:
        _geometry_store["agents"][agent_id]["position"] = position.dict()

    return {"status": "updated", "new_position": position}
