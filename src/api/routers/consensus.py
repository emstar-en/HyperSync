from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import uuid
from ..models import TransactionSubmission, TransactionResponse, ConsensusMetrics

router = APIRouter(
    prefix="/consensus",
    tags=["consensus"]
)

# In-memory mock store
_consensus_state = {
    "metrics": {
        "global_entropy": 0.15,
        "average_drift": 0.05,
        "active_spatial_quorums": 3
    },
    "transactions": {}
}

@router.post("/submit", response_model=TransactionResponse)
async def submit_transaction(submission: TransactionSubmission):
    """
    Submit a transaction proposal to the geometry engine for consensus.
    """
    tx_id = str(uuid.uuid4())

    # Simulate geometric cost calculation
    # Cost increases with entropy
    cost = 0.01 * _consensus_state["metrics"]["global_entropy"] * 100

    _consensus_state["transactions"][tx_id] = {
        "payload": submission.payload,
        "sender": submission.sender_id,
        "status": "pending_tier_1"
    }

    return TransactionResponse(
        tx_id=tx_id,
        status="pending_tier_1",
        estimated_cost=cost
    )

@router.get("/metrics", response_model=ConsensusMetrics)
async def get_consensus_metrics():
    """
    Get current system-wide consensus health metrics.
    """
    return _consensus_state["metrics"]

@router.post("/metrics/update")
async def update_metrics(metrics: ConsensusMetrics):
    """
    Force update metrics (Simulation hook).
    """
    _consensus_state["metrics"] = metrics.dict()
    return {"status": "updated"}
