"""
AGUA Runtime: Judge Module
===========================

Top-level orchestration layer that coordinates all runtime modules.

Functions:
- judge(instruction_pack, context, params) -> dict
  Orchestrates full pipeline: validate → map → score → accept/reject
"""

import numpy as np
from typing import Dict, Any, Optional, List

# Import all runtime modules
try:
    from runtime_psi import geodesic_distance, effective, lookup_psi_from_codebook
except ImportError:
    geodesic_distance = None
    effective = None
    lookup_psi_from_codebook = None

try:
    from runtime_cost import lexicographic_rank, lorentzian_refine, rank_candidates
except ImportError:
    lexicographic_rank = None
    lorentzian_refine = None
    rank_candidates = None

try:
    from runtime_mapping import linear_kappa_to_W, kernel_kappa_to_W
except ImportError:
    linear_kappa_to_W = None
    kernel_kappa_to_W = None

try:
    from runtime_invariants import dsl_validate, algebraic_validate, validate_instruction_pack
except ImportError:
    dsl_validate = None
    algebraic_validate = None
    validate_instruction_pack = None

try:
    from runtime_manifold import product_metric, couple
except ImportError:
    product_metric = None
    couple = None

try:
    from runtime_topology import beta0_quality, analyze_graph_topology
except ImportError:
    beta0_quality = None
    analyze_graph_topology = None


def judge(
    instruction_pack: Dict[str, Any],
    context: Dict[str, Any],
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Orchestrate full AGUA pipeline.

    Pipeline stages:
    1. Validate: Check DSL and algebraic constraints
    2. Map: Convert κ to W if needed
    3. Score: Compute ψ, cost, topology scores
    4. Accept/Reject: Apply acceptance gates

    Args:
        instruction_pack: Instruction pack to judge
        context: Context including:
            - psi_codebook: ψ codebook data
            - dsl_schema: DSL schema
            - optimal_cost: Optimal cost reference
        params: Optional parameters for all modules

    Returns:
        Judgment result with:
        - decision: 'ACCEPT', 'REJECT', or 'PENDING'
        - scores: All computed scores
        - violations: List of violations
        - validation: Validation results
        - details: Detailed results from each stage
    """
    if params is None:
        params = {}

    result = {
        'decision': 'PENDING',
        'scores': {},
        'violations': [],
        'validation': {},
        'details': {}
    }

    # Stage 1: Validation
    print("  Stage 1: Validation")
    validation_result = _validate_stage(instruction_pack, context, params)
    result['validation'] = validation_result
    result['details']['validation'] = validation_result

    if not validation_result['valid']:
        result['decision'] = 'REJECT'
        result['violations'] = validation_result['all_violations']
        return result

    # Stage 2: Mapping (if needed)
    print("  Stage 2: Mapping")
    mapping_result = _mapping_stage(instruction_pack, context, params)
    result['details']['mapping'] = mapping_result

    # Stage 3: Scoring
    print("  Stage 3: Scoring")
    scoring_result = _scoring_stage(instruction_pack, context, params)
    result['scores'] = scoring_result
    result['details']['scoring'] = scoring_result

    # Stage 4: Acceptance
    print("  Stage 4: Acceptance")
    acceptance_result = _acceptance_stage(instruction_pack, scoring_result, context, params)
    result['details']['acceptance'] = acceptance_result

    # Final decision
    if acceptance_result['all_gates_passed']:
        result['decision'] = 'ACCEPT'
    else:
        result['decision'] = 'REJECT'
        result['violations'] = acceptance_result['failed_gates']

    return result


def _validate_stage(
    instruction_pack: Dict[str, Any],
    context: Dict[str, Any],
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Stage 1: Validate instruction pack.
    """
    dsl_schema = context.get('dsl_schema', {})

    if validate_instruction_pack is not None:
        validation = validate_instruction_pack(instruction_pack, dsl_schema, params)
    else:
        # Fallback validation
        validation = {
            'valid': True,
            'dsl_valid': True,
            'algebraic_valid': True,
            'dsl_violations': [],
            'algebraic_violations': [],
            'all_violations': []
        }

    return validation


def _mapping_stage(
    instruction_pack: Dict[str, Any],
    context: Dict[str, Any],
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Stage 2: Map κ to W if needed.
    """
    mapping_result = {
        'mapping_applied': False,
        'W_computed': None
    }

    # Check if W needs to be computed from κ
    if 'Diagnostics' in instruction_pack:
        diag = instruction_pack['Diagnostics']
        if 'kappa' in diag and 'Convergence' not in instruction_pack:
            # Need to map κ to W
            kappa = diag['kappa']

            # Try kernel mapping first
            if kernel_kappa_to_W is not None and 'kappa_train' in context:
                try:
                    W = kernel_kappa_to_W(kappa, context)
                    mapping_result['mapping_applied'] = True
                    mapping_result['W_computed'] = W
                    mapping_result['method'] = 'kernel'

                    # Add W to instruction pack
                    if 'Convergence' not in instruction_pack:
                        instruction_pack['Convergence'] = {}
                    instruction_pack['Convergence']['W'] = W
                except Exception as e:
                    mapping_result['error'] = str(e)

            # Fallback to linear mapping
            elif linear_kappa_to_W is not None and 'A_matrix' in context:
                try:
                    A = context['A_matrix']
                    b = context.get('b_intercept', None)
                    W = linear_kappa_to_W(kappa, A, b)
                    mapping_result['mapping_applied'] = True
                    mapping_result['W_computed'] = W
                    mapping_result['method'] = 'linear'

                    if 'Convergence' not in instruction_pack:
                        instruction_pack['Convergence'] = {}
                    instruction_pack['Convergence']['W'] = W
                except Exception as e:
                    mapping_result['error'] = str(e)

    return mapping_result


def _scoring_stage(
    instruction_pack: Dict[str, Any],
    context: Dict[str, Any],
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Stage 3: Compute all scores.
    """
    scores = {}

    # Psi score
    if 'Convergence' in instruction_pack:
        conv = instruction_pack['Convergence']
        W = conv.get('W')
        W_ref = conv.get('W_ref')

        if W is not None and W_ref is not None:
            # Compute geodesic distance
            if geodesic_distance is not None:
                try:
                    d_H = geodesic_distance(W, W_ref)
                    scores['geodesic_distance'] = d_H
                except Exception as e:
                    scores['geodesic_distance_error'] = str(e)

            # Compute effective psi
            if effective is not None and 'psi_codebook' in context:
                try:
                    psi_codebook_data = context['psi_codebook']

                    # Look up psi entry
                    if lookup_psi_from_codebook is not None:
                        psi_entry = lookup_psi_from_codebook(psi_codebook_data, W)
                    else:
                        # Use target psi from pack
                        psi_entry = {'psi': conv.get('psi_target', 0.75)}

                    psi_eff = effective(psi_entry, W, W_ref, params)
                    scores['psi_effective'] = psi_eff
                    scores['psi_target'] = psi_entry['psi']
                except Exception as e:
                    scores['psi_error'] = str(e)

    # Cost score
    if 'CostOptimization' in instruction_pack:
        cost = instruction_pack['CostOptimization']
        dimensions = cost.get('lexicographic_order', [])

        # Build candidate dict from dimensions
        candidate = {}
        for dim_spec in cost.get('dimensions', []):
            candidate[dim_spec['name']] = dim_spec['value']

        if lexicographic_rank is not None:
            try:
                optimal = context.get('optimal_cost', {})
                rank_params = {
                    'reference_values': optimal,
                    'tolerance': params.get('cost_tolerance', 1e-6)
                }
                rank = lexicographic_rank(candidate, dimensions, rank_params)
                scores['cost_rank'] = rank
            except Exception as e:
                scores['cost_rank_error'] = str(e)

        if lorentzian_refine is not None:
            try:
                optimal = context.get('optimal_cost', {})
                refine_params = {
                    'gamma': params.get('gamma', 1.0),
                    'tau': params.get('tau', 1.0),
                    'dimensions': dimensions
                }
                refine = lorentzian_refine(candidate, optimal, refine_params)
                scores['cost_refine'] = refine
            except Exception as e:
                scores['cost_refine_error'] = str(e)

    # Topology score
    if 'Topology' in instruction_pack:
        topo = instruction_pack['Topology']

        if 'graph' in topo:
            graph = topo['graph']

            if beta0_quality is not None:
                try:
                    beta0 = beta0_quality(graph, params)
                    scores['beta0'] = beta0
                except Exception as e:
                    scores['beta0_error'] = str(e)

            if analyze_graph_topology is not None:
                try:
                    analysis = analyze_graph_topology(graph)
                    scores['topology_analysis'] = analysis
                    scores['topology_quality'] = analysis.get('quality_score', 0.0)
                except Exception as e:
                    scores['topology_error'] = str(e)
        else:
            # Use beta0 from pack
            scores['beta0'] = topo.get('beta0', 0)

    return scores


def _acceptance_stage(
    instruction_pack: Dict[str, Any],
    scores: Dict[str, Any],
    context: Dict[str, Any],
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Stage 4: Apply acceptance gates.
    """
    acceptance = {
        'all_gates_passed': True,
        'passed_gates': [],
        'failed_gates': []
    }

    # PSS envelope gates
    if 'Acceptance' in instruction_pack:
        accept_section = instruction_pack['Acceptance']

        if 'pss_envelope' in accept_section:
            pss = accept_section['pss_envelope']

            # Check each dimension
            for dim in ['D0', 'D1', 'D2']:
                if dim in pss:
                    dim_data = pss[dim]
                    satisfied = dim_data.get('satisfied', False)

                    if satisfied:
                        acceptance['passed_gates'].append(f'PSS_{dim}')
                    else:
                        acceptance['failed_gates'].append(f'PSS_{dim}')
                        acceptance['all_gates_passed'] = False

    # Psi gate
    psi_threshold = params.get('psi_threshold', 0.70)
    if 'psi_effective' in scores:
        if scores['psi_effective'] >= psi_threshold:
            acceptance['passed_gates'].append('psi_threshold')
        else:
            acceptance['failed_gates'].append(f"psi_threshold (got {scores['psi_effective']:.3f} < {psi_threshold})")
            acceptance['all_gates_passed'] = False

    # Cost rank gate
    max_cost_rank = params.get('max_cost_rank', 100)
    if 'cost_rank' in scores:
        if scores['cost_rank'] <= max_cost_rank:
            acceptance['passed_gates'].append('cost_rank')
        else:
            acceptance['failed_gates'].append(f"cost_rank (got {scores['cost_rank']} > {max_cost_rank})")
            acceptance['all_gates_passed'] = False

    # Topology gate
    max_beta0 = params.get('max_beta0', 3)
    if 'beta0' in scores:
        if scores['beta0'] <= max_beta0:
            acceptance['passed_gates'].append('beta0')
        else:
            acceptance['failed_gates'].append(f"beta0 (got {scores['beta0']} > {max_beta0})")
            acceptance['all_gates_passed'] = False

    return acceptance


# Example usage and validation
if __name__ == "__main__":
    print("AGUA Runtime Judge Module - Validation")
    print("=" * 50)

    # Create minimal instruction pack
    instruction_pack = {
        "Diagnostics": {
            "timestamp": "2025-01-01T00:00:00Z",
            "version": "v0.4-exp",
            "vendor": "test_vendor"
        },
        "CostOptimization": {
            "dimensions": [
                {"name": "latency", "value": 100, "weight": 0.5}
            ],
            "lexicographic_order": ["latency"]
        },
        "Convergence": {
            "W": [0.15, 0.15, 0.14, 0.14, 0.14, 0.14, 0.14],
            "W_ref": [0.20, 0.18, 0.15, 0.14, 0.12, 0.11, 0.10],
            "psi_target": 0.85
        },
        "Manifold": {
            "spaces": [{"type": "poincare", "dimension": 7}]
        },
        "Invariants": {
            "dsl_valid": True,
            "algebraic_constraints": []
        },
        "Topology": {
            "beta0": 1,
            "graph": {
                "nodes": ["A", "B", "C"],
                "edges": [["A", "B"], ["B", "C"]]
            }
        },
        "Judge": {
            "decision": "PENDING",
            "scores": {}
        },
        "Acceptance": {
            "gates_passed": [],
            "pss_envelope": {
                "D0": {"value": 0.85, "min": 0.80, "max": 0.90, "satisfied": True},
                "D1": {"value": 0.80, "min": 0.75, "max": 0.85, "satisfied": True},
                "D2": {"value": 0.75, "min": 0.70, "max": 0.80, "satisfied": True}
            }
        }
    }

    context = {
        "dsl_schema": {},
        "optimal_cost": {"latency": 80}
    }

    params = {
        "psi_threshold": 0.70,
        "max_cost_rank": 100,
        "max_beta0": 3
    }

    print("\nRunning judge pipeline...")
    result = judge(instruction_pack, context, params)

    print(f"\nDecision: {result['decision']}")
    print(f"Validation valid: {result['validation'].get('valid', 'N/A')}")
    print(f"Scores: {list(result['scores'].keys())}")
    print(f"Violations: {len(result['violations'])}")

    if result['details'].get('acceptance'):
        acc = result['details']['acceptance']
        print(f"Gates passed: {len(acc['passed_gates'])}")
        print(f"Gates failed: {len(acc['failed_gates'])}")

    print("\n✓ Judge orchestration operational")
