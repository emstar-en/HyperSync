"""HyperSync Core - Open Source Geometric Operations Library

Core tier (Free) implementation with 43 operations:
- 28 Geometry Operations (14 Hyperbolic + 14 Spherical)
- 5 Consensus Mechanisms
- 6 Security Modules
- 4 Heuristic Methods

All operations are O(n) or O(n log n) complexity.
"""

__version__ = "1.0.0"
__author__ = "HyperSync Team"
__license__ = "Apache 2.0"

from . import geometry
from . import consensus
from . import security
from . import heuristics

__all__ = [
    "geometry",
    "consensus",
    "security",
    "heuristics",
]
