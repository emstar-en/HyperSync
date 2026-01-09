"""Consensus & Attestation API"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from .consensus_manager import ConsensusAttestationManager

router = APIRouter(prefix="/api/v1/consensus", tags=["consensus"])
manager = ConsensusAttestationManager()

class ApplyConsensusRequest(BaseModel):
    target_type: str
    target_id: str
    mechanism_id: str
    parameters: Optional[Dict] = None
    nodes: Optional[List[str]] = None

class ApplyAttestationRequest(BaseModel):
    target_type: str
    target_id: str
    protocol_id: str
    verification_level: Optional[str] = None
    parameters: Optional[Dict] = None
    attestation_frequency: Optional[Dict] = None

@router.get("/mechanisms")
async def list_mechanisms(mechanism_type: Optional[str] = None):
    """List consensus mechanisms"""
    mechanisms = manager.list_consensus_mechanisms(mechanism_type=mechanism_type)
    return {"status": "success", "mechanisms": [m.__dict__ for m in mechanisms]}

@router.get("/mechanisms/{mechanism_id}")
async def get_mechanism(mechanism_id: str):
    """Get consensus mechanism"""
    mech = manager.get_consensus_mechanism(mechanism_id)
    if not mech:
        raise HTTPException(status_code=404, detail="Mechanism not found")
    return {"status": "success", "mechanism": mech.__dict__}

@router.post("/apply")
async def apply_consensus(request: ApplyConsensusRequest):
    """Apply consensus to target"""
    try:
        config = manager.apply_consensus(
            target_type=request.target_type,
            target_id=request.target_id,
            mechanism_id=request.mechanism_id,
            parameters=request.parameters,
            nodes=request.nodes
        )
        return {"status": "success", "config_id": config.config_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/config/{target_type}/{target_id}")
async def get_consensus_config(target_type: str, target_id: str):
    """Get consensus configuration"""
    config = manager.get_consensus_config(target_type, target_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return {"status": "success", "config": config.__dict__}

@router.get("/protocols")
async def list_protocols(protocol_type: Optional[str] = None):
    """List attestation protocols"""
    protocols = manager.list_attestation_protocols(protocol_type=protocol_type)
    return {"status": "success", "protocols": [p.__dict__ for p in protocols]}

@router.get("/protocols/{protocol_id}")
async def get_protocol(protocol_id: str):
    """Get attestation protocol"""
    proto = manager.get_attestation_protocol(protocol_id)
    if not proto:
        raise HTTPException(status_code=404, detail="Protocol not found")
    return {"status": "success", "protocol": proto.__dict__}

@router.post("/attestation/apply")
async def apply_attestation(request: ApplyAttestationRequest):
    """Apply attestation to target"""
    try:
        config = manager.apply_attestation(
            target_type=request.target_type,
            target_id=request.target_id,
            protocol_id=request.protocol_id,
            verification_level=request.verification_level,
            parameters=request.parameters,
            attestation_frequency=request.attestation_frequency
        )
        return {"status": "success", "config_id": config.config_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/attestation/config/{target_type}/{target_id}")
async def get_attestation_config(target_type: str, target_id: str):
    """Get attestation configuration"""
    config = manager.get_attestation_config(target_type, target_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return {"status": "success", "config": config.__dict__}

def register_api(app):
    """Register consensus API routes"""
    app.include_router(router)
