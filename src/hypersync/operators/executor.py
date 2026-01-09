from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import importlib.util
import traceback

from ..core.models import Intent

"""
Mathematical Foundations:
Orchestrates the execution of geometric operators.
Maps abstract operator IDs (e.g., 'op://pdhg.0') to concrete implementations.
Handles parameter validation and dispatch.

Fault Detection Logic:
- Validates existence of modules and functions.
- Checks required parameters for each operator.
- Implements fallback mechanisms (External -> Internal -> Pure Python if needed).
- Captures and re-raises execution errors with context.

Detailed Mechanisms:
1. Parse Intent to identify operator ID.
2. Resolve operator to file path (spec-pack or local tools).
3. Load module dynamically.
4. Execute function with parameters.
5. If external tool fails, attempt internal fallback (e.g., numpy implementation).
"""

_OP_MAP = {
    'op://sinkhorn_entropic.0': ('tools/solvers/ot/sinkhorn.py', 'sinkhorn'),
    'op://pdhg.0': ('tools/solvers/prox/pdhg.py', 'pdhg'),
    'op://geodesic_fast_marching.0': ('tools/solvers/geodesic_fast_marching.py', 'solve_eikonal'),
}

class OperatorExecutionError(Exception):
    pass

class OperatorExecutor:
    def __init__(self, spec_root: Path):
        self.spec_root = spec_root

    def _load_function(self, rel_module_path: str, func_name: str):
        mod_path = self.spec_root / rel_module_path
        if not mod_path.exists():
            alt = self.spec_root / ("spec-pack/" + rel_module_path)
            if alt.exists():
                mod_path = alt
        if not mod_path.exists():
            raise OperatorExecutionError(f"Module not found: {mod_path}")
        spec = importlib.util.spec_from_file_location(f"hypersync_ext.{mod_path.stem}", mod_path)
        if spec is None or spec.loader is None:
            raise OperatorExecutionError(f"Could not load module spec for {mod_path}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        func = getattr(mod, func_name, None)
        if func is None:
            raise OperatorExecutionError(f"Function {func_name} not found in {mod_path}")
        return func

    def run(self, op_id: str, intent: Intent) -> Dict[str, Any]:
        p = intent.params

        if 'sinkhorn_greenkhorn' in op_id:
            required = ['a', 'b', 'C', 'epsilon']
            missing = [n for n in required if p.get(n) is None]
            if missing:
                raise OperatorExecutionError(f"Missing parameters for greenkhorn: {', '.join(missing)}")
            try:
                func = self._load_function('tools/solvers/ot/sinkhorn.py', 'greenkhorn')
                res = func(p['a'], p['b'], p['C'], p['epsilon'], p.get('max_iters', 50000), p.get('tol', 1e-8))
            except Exception:
                from .algos import sinkhorn_greenkhorn
                res = sinkhorn_greenkhorn(p['a'], p['b'], p['C'], p['epsilon'], p.get('max_iters', 50000), p.get('tol', 1e-8))
            return {'transport_plan': res}

        if 'sinkhorn_unbalanced' in op_id:
            required = ['a', 'b', 'C', 'epsilon', 'tau_a', 'tau_b']
            missing = [n for n in required if p.get(n) is None]
            if missing:
                raise OperatorExecutionError(f"Missing parameters for unbalanced sinkhorn: {', '.join(missing)}")
            try:
                func = self._load_function('tools/solvers/ot/sinkhorn.py', 'sinkhorn_unbalanced')
                res = func(p['a'], p['b'], p['C'], p['epsilon'], p['tau_a'], p['tau_b'], p.get('max_iters', 10000), p.get('tol', 1e-8))
            except Exception:
                from .algos import sinkhorn_unbalanced
                res = sinkhorn_unbalanced(p['a'], p['b'], p['C'], p['epsilon'], p['tau_a'], p['tau_b'], p.get('max_iters', 10000), p.get('tol', 1e-8))
            return {'transport_plan': res}

        if 'sinkhorn_entropic' in op_id:
            required = ['a', 'b', 'C', 'epsilon']
            missing = [n for n in required if p.get(n) is None]
            if missing:
                raise OperatorExecutionError(f"Missing parameters for sinkhorn: {', '.join(missing)}")
            try:
                func = self._load_function(*_OP_MAP['op://sinkhorn_entropic.0'])
                res = func(p['a'], p['b'], p['C'], p['epsilon'], p.get('max_iters', 10000), p.get('tol', 1e-9), p.get('stabilized', True))
            except Exception:
                from .algos import sinkhorn_entropic
                res = sinkhorn_entropic(p['a'], p['b'], p['C'], p['epsilon'], p.get('max_iters', 10000), p.get('tol', 1e-9), p.get('stabilized', True))
            return {'transport_plan': res}

        if op_id.endswith('pdhg.0') or 'pdhg' in op_id:
            grad_terms = p.get('grad_terms')
            prox_terms = p.get('prox_terms')
            if grad_terms is not None and prox_terms is not None and p.get('tau') is not None and p.get('sigma') is not None:
                try:
                    func = self._load_function(*_OP_MAP['op://pdhg.0'])
                    res = func(grad_terms, prox_terms, p['tau'], p['sigma'], theta=p.get('theta', 1.0), max_iters=p.get('max_iters', 1000), tol=p.get('tol', 1e-6))
                    return {'solution': res}
                except Exception:
                    pass
            from .pdhg_numpy import pdhg_solve
            if p.get('A') is None or p.get('b') is None:
                raise OperatorExecutionError('PDHG fallback requires at least A and b; set lam and penalty/preset')
            fres = pdhg_solve(p)
            return {'solution': fres}

        if 'geodesic_fast_marching' in op_id:
            required = ['index_of_refraction', 'sources']
            missing = [n for n in required if p.get(n) is None]
            if missing:
                raise OperatorExecutionError(f"Missing parameters for fast marching: {', '.join(missing)}")
            try:
                func = self._load_function(*_OP_MAP['op://geodesic_fast_marching.0'])
                res = func(p['index_of_refraction'], p['sources'])
            except Exception:
                from .geodesic_numpy import solve_eikonal_grid
                res = solve_eikonal_grid(p['index_of_refraction'], p['sources'])
            return {'eikonal_solution': res}

        if 'pdhg_tv_denoise' in op_id:
            if p.get('image') is None:
                raise OperatorExecutionError('TV denoise requires parameter: image (2D array)')
            try:
                func = self._load_function('tools/solvers/prox/pdhg_tv.py', 'pdhg_tv')
                res = func(p)
                return {'denoised': res}
            except Exception:
                from .pdhg_tv_numpy import pdhg_tv_denoise
                fres = pdhg_tv_denoise(p)
                return {'denoised': fres}

        key = op_id
        if key not in _OP_MAP:
            base = op_id.split('@')[0]
            key = base if base in _OP_MAP else key
        mapping = _OP_MAP.get(key)
        if not mapping:
            raise OperatorExecutionError(f"No executor mapping for {op_id}")
        func = self._load_function(*mapping)
        try:
            return func(intent)
        except Exception as e:
            raise OperatorExecutionError(str(e))
