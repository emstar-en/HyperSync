from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Point(BaseModel):
    x: float
    y: float

class PolarCoordinate(BaseModel):
    r: float
    theta: float

class SectorState(BaseModel):
    sector_id: str
    coordinator_id: str
    boundary_points: List[Point]
    worker_count: int
    density: float

class AgentPosition(BaseModel):
    agent_id: str
    position: PolarCoordinate
    drift_vector: float
    status: str

class TransactionSubmission(BaseModel):
    payload: Dict[str, Any] = Field(..., description="Arbitrary transaction payload")
    sender_id: str

class TransactionResponse(BaseModel):
    tx_id: str
    status: str
    estimated_cost: float

class ConsensusMetrics(BaseModel):
    global_entropy: float
    average_drift: float
    active_spatial_quorums: int
