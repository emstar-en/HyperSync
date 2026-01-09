
from enum import Enum
from pydantic import BaseModel
from typing import Any, Dict, List

class ConsensusState(str, Enum):
    PROPOSED = "PROPOSED"
    VOTING = "VOTING"
    COMMITTED = "COMMITTED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"

class Vote(BaseModel):
    voter_id: str
    approve: bool
    reason: str = ""

class Transaction(BaseModel):
    id: str
    initiator_id: str
    payload: Any
    state: ConsensusState
    votes: List[Vote] = []
    quorum_id: str = ""
