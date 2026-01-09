"""
AGUA Runtime Modules
====================

All runtime modules for AGUA governance system.

Modules:
- runtime_psi: Geodesic distance and effective ψ
- runtime_cost: Lexicographic ranking and Lorentzian refinement
- runtime_mapping: κ→W mapping
- runtime_invariants: DSL and algebraic validation
- runtime_manifold: Product manifold operations
- runtime_topology: Topological quality metrics
- runtime_judge: Orchestration layer (main entry point)
"""

__all__ = [
    'runtime_psi',
    'runtime_cost',
    'runtime_mapping',
    'runtime_invariants',
    'runtime_manifold',
    'runtime_topology',
    'runtime_judge'
]
