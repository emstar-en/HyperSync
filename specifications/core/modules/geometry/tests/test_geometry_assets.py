import json, os
def exists(p):
    return os.path.exists(p)
required = [
    'schemas/geometry/tensor_calculus.schema.json',
    'schemas/geometry/differential_forms.schema.json',
    'schemas/geometry/riemannian_geometry.schema.json',
    'schemas/geometry/lie_groups.schema.json',
    'schemas/geometry/fiber_bundles.schema.json',
    'schemas/geometry/gauge_theory.schema.json',
    'schemas/geometry/algorithm_ids.schema.json',
    'modules/geometry/docs/tensor_calculus.md',
    'modules/geometry/docs/differential_forms.md',
    'modules/geometry/docs/riemannian_geometry.md',
    'modules/geometry/docs/lie_groups.md',
    'modules/geometry/docs/fiber_bundles.md',
    'modules/geometry/docs/gauge_theory.md'
]
missing = [p for p in required if not exists(p)]
print(json.dumps({'ok': len(missing)==0, 'missing': missing}))
if missing:
    raise SystemExit(1)
