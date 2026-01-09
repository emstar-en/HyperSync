from .commit_tools import canonical_json_hash

def make_reduction_receipt(inputs, solver_binding_id, iters, residuals, outputs):
    return {
        'inputs_commitment': canonical_json_hash(inputs),
        'solver_binding_id': solver_binding_id,
        'iters': iters,
        'residuals': residuals,
        'output_commitment': canonical_json_hash(outputs)
    }

