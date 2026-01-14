"""Consensus Mechanisms Module

Provides 5 Core tier consensus mechanisms:
1. Raft - Leader-based consensus
2. Paxos - Classic Byzantine consensus
3. Spherical BFT - O(n) geometric Byzantine fault tolerance
4. Poincaré Voting - Hyperbolic distance-based voting
5. Sampling-Based Consensus - Fast O(n) approximate consensus

All mechanisms designed for f < n/3 Byzantine tolerance.
"""

from .raft import raft_consensus
from .paxos import paxos_consensus
from .spherical_bft import spherical_bft_consensus
from .poincare_voting import poincare_voting_consensus
from .sampling_consensus import sampling_consensus

__all__ = [
    "raft_consensus",
    "paxos_consensus",
    "spherical_bft_consensus",
    "poincare_voting_consensus",
    "sampling_consensus",
]
