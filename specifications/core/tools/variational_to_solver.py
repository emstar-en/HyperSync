#!/usr/bin/env python3
import json, sys

DEFAULTS = {
  'eikonal→geodesics': {'solver':'fast_marching','backend':'cpu','params':{}},
  'entropy→wasserstein': {'solver':'jko_prox','backend':'cpu','params':{'tau':1.0}},
  'euler→sdiff': {'solver':'symplectic','backend':'cpu','params':{'scheme':'implicit-midpoint'}},
  'hamiltonian→symplectic': {'solver':'symplectic','backend':'cpu','params':{'scheme':'leapfrog'}}
}

if __name__ == '__main__':
    plan = json.load(sys.stdin)
    bind = DEFAULTS.get(plan.get('mapping','custom'), {'solver':'custom','backend':'cpu','params':{}})
    plan['solverBinding'] = bind
    json.dump(plan, sys.stdout, indent=2)


# ---- Bindings for optimization/VI/OT/relaxations ----
BINDINGS_EXT = {
  'prox/fista': {'solver':'solver://prox/fista','backend':'cpu','params':{'step_size':'backtracking','momentum':True}},
  'prox/admm': {'solver':'solver://prox/admm','backend':'cpu','params':{'rho':1.0}},
  'prox/pdhg': {'solver':'solver://prox/pdhg','backend':'cpu','params':{'tau':0.9,'sigma':0.9,'theta':1.0}},
  'prox/pnp': {'solver':'solver://prox/pnp','backend':'cpu','params':{'sigma':0.01}},
  'prox/red': {'solver':'solver://prox/red','backend':'cpu','params':{'lambda':0.1,'step_size':1.0}},

  'convex/cvxpy.osqp.qp': {'solver':'solver://convex/cvxpy.osqp.qp','backend':'cpu','params':{'max_iters':5000}},
  'convex/cvxpy.ecos.socp': {'solver':'solver://convex/cvxpy.ecos.socp','backend':'cpu','params':{'max_iters':5000}},
  'convex/sdp.scs': {'solver':'solver://convex/sdp.scs','backend':'cpu','params':{'max_iters':5000}},

  'vi/mfvi.prox': {'solver':'solver://vi/mfvi.prox','backend':'cpu','params':{'natural_grad':True}},
  'vi/ep.fixed_point': {'solver':'solver://vi/ep.fixed_point','backend':'cpu','params':{'damping':0.5}},
  'vi/laplace.newton': {'solver':'solver://vi/laplace.newton','backend':'cpu','params':{'hessian_reg':1e-6}},

  'ot/sinkhorn': {'solver':'solver://ot/sinkhorn','backend':'cpu','params':{'stabilized':True}},
  'ot/unbalanced_sinkhorn': {'solver':'solver://ot/unbalanced_sinkhorn','backend':'cpu','params':{}},
  'ot/jko_step': {'solver':'solver://ot/jko_step','backend':'cpu','params':{'step_size':1.0}},
  'ot/semi_discrete': {'solver':'solver://ot/semi_discrete','backend':'cpu','params':{}},

  'relax/sdp.maxcut': {'solver':'solver://relax/sdp.maxcut','backend':'cpu','params':{'rank_recovery':'none'}},
  'relax/mccormick': {'solver':'solver://relax/mccormick','backend':'cpu','params':{'tightening_iters':0}},
  'relax/lp_mip_relax': {'solver':'solver://relax/lp_mip_relax','backend':'cpu','params':{'gap_tolerance':0.01}}
}
