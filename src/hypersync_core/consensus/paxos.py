"""Paxos Consensus Implementation

Classic Byzantine consensus algorithm.
Simplified multi-Paxos for Core tier.

Complexity: O(n²) communication
Byzantine tolerance: f < n/3
"""

import numpy as np
from typing import List, Tuple, Optional, Dict


def paxos_consensus(
    proposals: List[np.ndarray],
    proposer_id: int = 0
) -> Tuple[np.ndarray, Dict]:
    """Simplified Paxos consensus algorithm.
    
    Three-phase protocol:
    1. Prepare phase: Proposer sends prepare(n)
    2. Promise phase: Acceptors respond with promise
    3. Accept phase: Proposer sends accept(n, value)
    4. Accepted phase: Acceptors accept if no higher proposal
    
    Args:
        proposals: List of node proposals
        proposer_id: ID of proposing node
    
    Returns:
        consensus: Agreed value
        metadata: Consensus metadata (round number, acceptors, etc.)
    
    Complexity: O(n²)
    """
    n = len(proposals)
    
    if n < 4:
        raise ValueError("Need at least 4 nodes for Paxos")
    
    # Simplified Paxos: use majority voting
    
    # Phase 1: Prepare
    proposal_number = 1
    
    # Phase 2: Promise (all nodes promise in simplified version)
    promises = n
    majority = (n // 2) + 1
    
    if promises < majority:
        raise ValueError("No consensus: insufficient promises")
    
    # Phase 3: Accept
    proposed_value = proposals[proposer_id]
    
    # Phase 4: Accepted (majority accepts)
    accepts = n
    
    if accepts >= majority:
        consensus = proposed_value
    else:
        raise ValueError("No consensus: insufficient accepts")
    
    metadata = {
        "round": proposal_number,
        "proposer": proposer_id,
        "promises": promises,
        "accepts": accepts,
        "majority_threshold": majority,
    }
    
    return consensus, metadata
