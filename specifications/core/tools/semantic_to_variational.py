#!/usr/bin/env python3
import json, sys

MAPPINGS = {
  'eikonal': 'eikonal→geodesics',
  'diffusion': 'entropy→wasserstein',
  'euler_incompressible': 'euler→sdiff',
  'hamiltonian': 'hamiltonian→symplectic'
}

def compile_intent(intent):
    obj = intent.get('objective','custom')
    mapping = MAPPINGS.get(obj, 'custom')
    if mapping == 'eikonal→geodesics':
        var = {'action':'∫ n(x)|∇T| dx','constraints':[],'discretization':'grid'}
    elif mapping == 'entropy→wasserstein':
        var = {'action':'Ent(ρ)','constraints':[],'discretization':'grid'}
    elif mapping == 'euler→sdiff':
        var = {'action':'∫ 1/2 |u|^2 dx','constraints':['div(u)=0'],'discretization':'DEC'}
    elif mapping == 'hamiltonian→symplectic':
        var = {'action':'∫ (p·dq - H dt)','constraints':[],'discretization':'particles'}
    else:
        var = {'action': intent.get('notes',''), 'constraints': intent.get('constraints',[]), 'discretization':'grid'}
    plan = {'type':'geometric.reduction.plan','mapping': mapping, 'variational': var}
    return plan

if __name__ == '__main__':
    intent = json.load(sys.stdin)
    plan = compile_intent(intent)
    json.dump(plan, sys.stdout, indent=2)


# ---- Extensions for optimization/VI/OT/relaxations ----
ADDITIONAL_MAPPINGS = {
  'lasso_regression': 'prox/fista',
  'generalized_l1_l2_minimization': 'prox/fista',
  'ot_barycenter': 'ot/sinkhorn',
  'ot_unbalanced_barycenter': 'ot/unbalanced_sinkhorn',
  'vi_mean_field': 'vi/mfvi.prox',
  'vi_ep': 'vi/ep.fixed_point',
  'vi_laplace': 'vi/laplace.newton',
  'combinatorial_relaxation': 'relax/sdp.maxcut'
}
