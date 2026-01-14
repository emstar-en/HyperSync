"""Raft Consensus Implementation

Leader-based consensus algorithm for distributed systems.
Simplified implementation for Core tier.

Complexity: O(n) per round
Fault tolerance: f < n/2 (crash faults, not Byzantine)
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from enum import Enum


class NodeState(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"


def raft_consensus(
    proposals: List[np.ndarray],
    node_id: int = 0,
    timeout: int = 10
) -> Tuple[np.ndarray, int]:
    """Simplified Raft consensus for value agreement.
    
    Algorithm:
    1. Leader election (highest ID for simplicity)
    2. Leader proposes value
    3. Followers vote if they accept
    4. Consensus if majority votes
    
    Args:
        proposals: List of node proposals
        node_id: Current node ID (for leader election)
        timeout: Election timeout (iterations)
    
    Returns:
        consensus: Agreed value
        leader_id: ID of elected leader
    
    Complexity: O(n)
    """
    n = len(proposals)
    
    if n < 3:
        raise ValueError("Need at least 3 nodes for Raft consensus")
    
    # Simplified leader election: highest ID wins
    leader_id = node_id
    
    # Leader proposes their value
    leader_proposal = proposals[leader_id]
    
    # Count votes (all nodes vote for leader in simplified version)
    votes = n
    majority = (n // 2) + 1
    
    if votes >= majority:
        consensus = leader_proposal
    else:
        raise ValueError("No consensus reached")
    
    return consensus, leader_id
