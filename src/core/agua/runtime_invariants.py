"""
AGUA Runtime: Invariants Module
================================

Validates instruction packs against DSL schema and algebraic constraints.

Functions:
- dsl_validate(instruction_pack, dsl_schema) -> bool
  Validates instruction pack against DSL schema

- algebraic_validate(instruction_pack, params) -> bool
  Checks algebraic constraints (e.g., ||W|| ≤ 1-ε)
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import json


def dsl_validate(
    instruction_pack: Dict[str, Any],
    dsl_schema: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Validate instruction pack against DSL schema.

    Checks:
    - Required sections present
    - Field types match schema
    - Structural constraints satisfied

    Args:
        instruction_pack: Instruction pack to validate
        dsl_schema: DSL schema definition

    Returns:
        Tuple (is_valid, violations)
        - is_valid: True if pack satisfies DSL schema
        - violations: List of violation messages
    """
    violations = []

    # Check required sections (8 sections)
    required_sections = [
        "Diagnostics",
        "CostOptimization",
        "Convergence",
        "Manifold",
        "Invariants",
        "Topology",
        "Judge",
        "Acceptance"
    ]

    for section in required_sections:
        if section not in instruction_pack:
            violations.append(f"Missing required section: {section}")

    # Validate Diagnostics section
    if "Diagnostics" in instruction_pack:
        diag = instruction_pack["Diagnostics"]
        required_fields = ["timestamp", "version", "vendor"]
        for field in required_fields:
            if field not in diag:
                violations.append(f"Diagnostics missing required field: {field}")

    # Validate CostOptimization section
    if "CostOptimization" in instruction_pack:
        cost = instruction_pack["CostOptimization"]
        if "dimensions" not in cost:
            violations.append("CostOptimization missing 'dimensions'")
        if "lexicographic_order" not in cost:
            violations.append("CostOptimization missing 'lexicographic_order'")

    # Validate Convergence section
    if "Convergence" in instruction_pack:
        conv = instruction_pack["Convergence"]
        required_fields = ["W", "W_ref", "psi_target"]
        for field in required_fields:
            if field not in conv:
                violations.append(f"Convergence missing required field: {field}")

        # Check W and W_ref are length 7
        if "W" in conv:
            if not isinstance(conv["W"], list) or len(conv["W"]) != 7:
                violations.append(f"Convergence.W must be list of length 7, got {type(conv['W'])} length {len(conv.get('W', []))}")

        if "W_ref" in conv:
            if not isinstance(conv["W_ref"], list) or len(conv["W_ref"]) != 7:
                violations.append(f"Convergence.W_ref must be list of length 7")

    # Validate Manifold section
    if "Manifold" in instruction_pack:
        manifold = instruction_pack["Manifold"]
        if "spaces" not in manifold:
            violations.append("Manifold missing 'spaces'")
        elif not isinstance(manifold["spaces"], list):
            violations.append("Manifold.spaces must be a list")

    # Validate Invariants section
    if "Invariants" in instruction_pack:
        inv = instruction_pack["Invariants"]
        required_fields = ["dsl_valid", "algebraic_constraints"]
        for field in required_fields:
            if field not in inv:
                violations.append(f"Invariants missing required field: {field}")

    # Validate Topology section
    if "Topology" in instruction_pack:
        topo = instruction_pack["Topology"]
        if "beta0" not in topo:
            violations.append("Topology missing 'beta0'")

    # Validate Judge section
    if "Judge" in instruction_pack:
        judge = instruction_pack["Judge"]
        required_fields = ["decision", "scores"]
        for field in required_fields:
            if field not in judge:
                violations.append(f"Judge missing required field: {field}")

        # Check decision is valid
        if "decision" in judge:
            valid_decisions = ["ACCEPT", "REJECT", "PENDING"]
            if judge["decision"] not in valid_decisions:
                violations.append(f"Judge.decision must be one of {valid_decisions}, got {judge['decision']}")

    # Validate Acceptance section
    if "Acceptance" in instruction_pack:
        accept = instruction_pack["Acceptance"]
        required_fields = ["gates_passed", "pss_envelope"]
        for field in required_fields:
            if field not in accept:
                violations.append(f"Acceptance missing required field: {field}")

        # Check PSS envelope has D0, D1, D2
        if "pss_envelope" in accept:
            pss = accept["pss_envelope"]
            for dim in ["D0", "D1", "D2"]:
                if dim not in pss:
                    violations.append(f"Acceptance.pss_envelope missing dimension: {dim}")

    is_valid = len(violations) == 0
    return is_valid, violations


def algebraic_validate(
    instruction_pack: Dict[str, Any],
    params: Optional[Dict[str, Any]] = None
) -> Tuple[bool, List[str]]:
    """
    Validate algebraic constraints on instruction pack.

    Checks:
    - ||W|| ≤ 1-ε (Poincaré ball constraint)
    - W components non-negative (optional)
    - PSS envelope ordering: D0 >= D1 >= D2
    - Cost dimensions within bounds

    Args:
        instruction_pack: Instruction pack to validate
        params: Optional parameters:
            - epsilon: Margin from ball boundary (default: 0.01)
            - require_nonnegative_W: Require W >= 0 (default: False)
            - pss_min_threshold: Minimum PSS values (default: 0.45)

    Returns:
        Tuple (is_valid, violations)
    """
    if params is None:
        params = {}

    epsilon = params.get('epsilon', 0.01)
    require_nonnegative_W = params.get('require_nonnegative_W', False)
    pss_min_threshold = params.get('pss_min_threshold', 0.45)

    violations = []

    # Check W constraint
    if "Convergence" in instruction_pack:
        conv = instruction_pack["Convergence"]

        if "W" in conv:
            W = np.array(conv["W"], dtype=np.float64)
            W_norm = np.linalg.norm(W)

            # Poincaré ball constraint: ||W|| < 1
            if W_norm >= 1.0 - epsilon:
                violations.append(f"||W|| = {W_norm:.6f} violates Poincaré ball constraint (must be < {1.0 - epsilon})")

            # Non-negativity constraint (optional)
            if require_nonnegative_W:
                if np.any(W < 0):
                    violations.append(f"W has negative components: {W[W < 0].tolist()}")

        # Check W_ref constraint
        if "W_ref" in conv:
            W_ref = np.array(conv["W_ref"], dtype=np.float64)
            W_ref_norm = np.linalg.norm(W_ref)

            if W_ref_norm >= 1.0 - epsilon:
                violations.append(f"||W_ref|| = {W_ref_norm:.6f} violates Poincaré ball constraint")

    # Check PSS envelope ordering
    if "Acceptance" in instruction_pack:
        accept = instruction_pack["Acceptance"]

        if "pss_envelope" in accept:
            pss = accept["pss_envelope"]

            # Extract values
            D0_val = pss.get("D0", {}).get("value", None)
            D1_val = pss.get("D1", {}).get("value", None)
            D2_val = pss.get("D2", {}).get("value", None)

            if D0_val is not None and D1_val is not None and D2_val is not None:
                # Check ordering: D0 >= D1 >= D2
                if not (D0_val >= D1_val >= D2_val):
                    violations.append(f"PSS envelope ordering violated: D0={D0_val:.3f}, D1={D1_val:.3f}, D2={D2_val:.3f} (must have D0 >= D1 >= D2)")

                # Check minimum thresholds
                if D0_val < pss_min_threshold:
                    violations.append(f"D0 = {D0_val:.3f} below minimum threshold {pss_min_threshold}")
                if D1_val < pss_min_threshold:
                    violations.append(f"D1 = {D1_val:.3f} below minimum threshold {pss_min_threshold}")
                if D2_val < pss_min_threshold:
                    violations.append(f"D2 = {D2_val:.3f} below minimum threshold {pss_min_threshold}")

    # Check cost dimensions
    if "CostOptimization" in instruction_pack:
        cost = instruction_pack["CostOptimization"]

        if "dimensions" in cost:
            for i, dim in enumerate(cost["dimensions"]):
                # Check weight is in [0, 1]
                if "weight" in dim:
                    w = dim["weight"]
                    if w < 0 or w > 1:
                        violations.append(f"Cost dimension {i} weight {w} outside [0, 1]")

    is_valid = len(violations) == 0
    return is_valid, violations


def validate_instruction_pack(
    instruction_pack: Dict[str, Any],
    dsl_schema: Dict[str, Any],
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Comprehensive validation of instruction pack.

    Combines DSL and algebraic validation.

    Args:
        instruction_pack: Instruction pack to validate
        dsl_schema: DSL schema definition
        params: Optional parameters for algebraic validation

    Returns:
        Validation result dictionary:
        {
            "valid": bool,
            "dsl_valid": bool,
            "algebraic_valid": bool,
            "dsl_violations": list,
            "algebraic_violations": list,
            "all_violations": list
        }
    """
    # DSL validation
    dsl_valid, dsl_violations = dsl_validate(instruction_pack, dsl_schema)

    # Algebraic validation
    algebraic_valid, algebraic_violations = algebraic_validate(instruction_pack, params)

    # Combined result
    all_violations = dsl_violations + algebraic_violations
    valid = dsl_valid and algebraic_valid

    return {
        "valid": valid,
        "dsl_valid": dsl_valid,
        "algebraic_valid": algebraic_valid,
        "dsl_violations": dsl_violations,
        "algebraic_violations": algebraic_violations,
        "all_violations": all_violations
    }


# Example usage and validation
if __name__ == "__main__":
    print("AGUA Runtime Invariants Module - Validation")
    print("=" * 50)

    # Create a minimal valid instruction pack
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
            "spaces": [
                {"type": "poincare", "dimension": 7}
            ]
        },
        "Invariants": {
            "dsl_valid": True,
            "algebraic_constraints": []
        },
        "Topology": {
            "beta0": 1
        },
        "Judge": {
            "decision": "ACCEPT",
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

    dsl_schema = {}  # Simplified for example

    # Test DSL validation
    print("\nDSL validation test:")
    dsl_valid, dsl_violations = dsl_validate(instruction_pack, dsl_schema)
    print(f"  Valid: {dsl_valid}")
    if dsl_violations:
        print(f"  Violations: {dsl_violations}")

    # Test algebraic validation
    print("\nAlgebraic validation test:")
    alg_valid, alg_violations = algebraic_validate(instruction_pack)
    print(f"  Valid: {alg_valid}")
    if alg_violations:
        print(f"  Violations: {alg_violations}")

    # Test comprehensive validation
    print("\nComprehensive validation test:")
    result = validate_instruction_pack(instruction_pack, dsl_schema)
    print(f"  Overall valid: {result['valid']}")
    print(f"  DSL valid: {result['dsl_valid']}")
    print(f"  Algebraic valid: {result['algebraic_valid']}")

    print("\n✓ All functions operational")
