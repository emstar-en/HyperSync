"""Heuristics Module

Provides 4 Core tier heuristic methods:
1. Ricci Flow Heuristic - O(n) fast approximation (10,000x speedup)
2. Proximity Adversarial Detection - Fast adversarial detection (included in security)
3. Fast Curvature Estimation - O(n) curvature approximation (1,000x speedup)
4. Sampling Consensus - O(n) fast consensus (included in consensus)

All heuristics trade perfect accuracy for speed (90-95%+ accuracy).
"""

from .ricci_flow import ricci_flow_heuristic, ricci_flow_ultra_fast
from .fast_curvature import fast_curvature_estimation, local_curvature_5point

__all__ = [
    "ricci_flow_heuristic",
    "ricci_flow_ultra_fast",
    "fast_curvature_estimation",
    "local_curvature_5point",
]
