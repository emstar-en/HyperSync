from __future__ import annotations
import numpy as np
from typing import Dict, Optional


def _arcosh(z: float) -> float:
    if z < 1.0:
        z = 1.0
    return float(np.log(z + np.sqrt(z*z - 1.0)))

class PoincareBall:
    """Poincaré ball model with curvature K<0 (default K=-1).
    Distances use the exact arcosh formula. Radius cap prevents leaving the ball.
    """
    def __init__(self, dim: int = 8, curvature: float = -1.0, radius_cap: float = 0.98):
        assert curvature < 0, 'curvature must be negative for hyperbolic Poincaré ball'
        self.dim = dim
        self.K = curvature
        self.radius_cap = radius_cap

    def dist(self, x: np.ndarray, y: np.ndarray) -> float:
        # Using K=-1 scaling. For K!= -1, scale by 1/sqrt(-K)
        nx2 = float(np.sum(x*x))
        ny2 = float(np.sum(y*y))
        diff2 = float(np.sum((x - y)*(x - y)))
        denom = (1.0 - nx2) * (1.0 - ny2)
        denom = max(denom, 1e-12)
        arg = 1.0 + 2.0 * diff2 / denom
        d = _arcosh(arg)
        scale = 1.0 / np.sqrt(-self.K)
        return float(d * scale)

    def project(self, x: np.ndarray) -> np.ndarray:
        r = self.radius_cap
        n = float(np.linalg.norm(x))
        if n == 0:
            return x
        if n >= r:
            return (x / n) * (r - 1e-6)
        return x

class EmbeddingStore:
    def __init__(self, dim: int = 8, curvature: float = -1.0, radius_cap: float = 0.98, seed: int = 0):
        self.ball = PoincareBall(dim, curvature, radius_cap)
        self.seed = seed
        self.vecs: Dict[str, np.ndarray] = {}

    def get(self, key: str) -> np.ndarray:
        if key not in self.vecs:
            h = abs(hash(key)) % (2**32)
            rng = np.random.default_rng(h ^ (self.seed & 0xFFFFFFFF))
            v = rng.normal(size=self.ball.dim)
            v = v / (np.linalg.norm(v) + 1e-12) * 0.2
            self.vecs[key] = self.ball.project(v)
        return self.vecs[key]

    def distance(self, a: str, b: str) -> float:
        return float(self.ball.dist(self.get(a), self.get(b)))
