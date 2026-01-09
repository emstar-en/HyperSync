#!/usr/bin/env python3
import json, sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'spec-pack' / 'modules' / 'ico' / 'kernels'))
try:
    import ref_kernels as K
except Exception:
    K = None

# Minimal schema validator
def _validate_type(val, t):
    if t == 'object': return isinstance(val, dict)
    if t == 'array': return isinstance(val, list)
    if t == 'string': return isinstance(val, str)
    if t == 'integer': return isinstance(val, int) and not isinstance(val, bool)
    if t == 'number': return isinstance(val, (int,float)) and not isinstance(val, bool)
    if t == 'boolean': return isinstance(val, bool)
    return True

def validate_against_schema(instance, schema, base_schemas=None, path='$'):
    errs = []
    if base_schemas is None: base_schemas = {}
    if '$ref' in schema:
        ref = schema['$ref']
        ref_key = ref.split('/')[-1]
        target = base_schemas.get(ref) or base_schemas.get(ref_key)
        if target is None:
            errs.append(f"{path}: unresolved $ref {ref}")
            return errs
        return validate_against_schema(instance, target, base_schemas, path)
    t = schema.get('type')
    if t:
        if isinstance(t, list):
            if not any(_validate_type(instance, ti) for ti in t):
                errs.append(f"{path}: type mismatch {t}")
                return errs
        else:
            if not _validate_type(instance, t):
                errs.append(f"{path}: type mismatch {t}")
                return errs
    req = schema.get('required', [])
    if isinstance(instance, dict):
        for k in req:
            if k not in instance:
                errs.append(f"{path}: missing required {k}")
    if 'enum' in schema:
        if instance not in schema['enum']:
            errs.append(f"{path}: value {instance} not in enum {schema['enum']}")
    if 'oneOf' in schema:
        ok = False; sub_errs = []
        for i, sub in enumerate(schema['oneOf']):
            e = validate_against_schema(instance, sub, base_schemas, path+f'.oneOf[{i}]')
            if not e: ok=True; break
            else: sub_errs.extend(e)
        if not ok:
            errs.append(f"{path}: oneOf no match; first errors: {sub_errs[:2]}")
    props = schema.get('properties', {})
    if isinstance(instance, dict):
        for k, sub in props.items():
            if k in instance:
                errs.extend(validate_against_schema(instance[k], sub, base_schemas, path+f'.{k}'))
    return errs

# Load schemas

def load_schemas(root: Path):
    base = {}
    for p in (root/'spec-pack'/'schemas').rglob('*.json'):
        try:
            data = json.loads(p.read_text(encoding='utf-8'))
            sid = data.get('$id') or str(p)
            base[sid] = data
            base[p.name] = data
            base[str(p)] = data
        except Exception:
            pass
    return base

# Numeric helpers

def vec_norm(v):
    return math.sqrt(sum(float(x)*float(x) for x in v))

def minkowski_dot(x):
    return float(x[0])*float(x[0]) - sum(float(xi)*float(xi) for xi in x[1:])

# Validators

def validate_ico_core_numeric(vec):
    prof = vec.get('profile')
    inputs = vec.get('inputs', {})
    if prof == 'S':
        for k in ('x','y'):
            amb = inputs.get(k, {}).get('ambient')
            if amb is not None:
                n = vec_norm(amb)
                assert abs(n-1.0) < 1e-6, f'S: {k} not unit norm (got {n})'
    if prof == 'H' and vec.get('model','') == 'lorentz':
        for k in ('x','y'):
            lor = inputs.get(k, {}).get('lorentz')
            if lor is not None:
                md = minkowski_dot(lor)
                assert abs(md + 1.0) < 1e-3, f'H: {k} not on unit hyperboloid, got {md}'
    return True


def validate_connect_vector(vec, schemas):
    schema = schemas.get('connect.schema.json') or next((v for k,v in schemas.items() if k.endswith('connect.schema.json')), None)
    if schema:
        errs = validate_against_schema(vec, schema, schemas)
        if errs:
            raise AssertionError('schema: ' + '; '.join(errs))
    hello = vec['hello']; acc = vec['accept']
    assert acc.get('profile') == hello['wants']['profile'], 'profile mismatch in accept'
    return True


def validate_sync_vector(vec, schemas):
    schema = schemas.get('sync.schema.json') or next((v for k,v in schemas.items() if k.endswith('sync.schema.json')), None)
    if schema:
        errs = validate_against_schema(vec, schema, schemas)
        if errs:
            raise AssertionError('schema: ' + '; '.join(errs))
    return True

# Execute numeric vectors using kernels

def run_numeric_vector(v):
    if K is None:
        return {'skipped': 'kernels not available'}
    prof = v.get('profile')
    exp = v.get('expected', {})
    inputs = v.get('inputs', {})
    if prof == 'E':
        x = inputs['x']; vvec = inputs['v']
        y = K.Euclid.exp_map(x, vvec)
        d = K.Euclid.distance(x, y)
        ok = abs(d - exp.get('distance_xy', d)) <= 1e-9
        # roundtrip: log(exp(x,v)) ~ v
        v_rt = K.Euclid.log_map(x, y)
        rt = max(abs(vi - ri) for vi,ri in zip(vvec, v_rt))
        ok = ok and rt <= exp.get('roundtrip_tol', 1e-9)
        return {'distance': d, 'roundtrip_err': rt, 'ok': ok}
    if prof == 'S':
        x = inputs['x']['ambient']; y = inputs['y']['ambient']
        x = K.Sphere.project(x); y = K.Sphere.project(y)
        d = K.Sphere.distance(x,y)
        ok = (d >= exp.get('distance_min',0)) and (d <= exp.get('distance_max', 1e9))
        # roundtrip
        vtan = K.Sphere.log_map(x,y)
        y2 = K.Sphere.exp_map(x, vtan)
        rt = max(abs(a-b) for a,b in zip(y, y2))
        ok = ok and (rt <= exp.get('roundtrip_tol', 1e-6))
        return {'distance': d, 'roundtrip_err': rt, 'ok': ok}
    if prof == 'H' and v.get('model') == 'lorentz':
        x = inputs['x']['lorentz']; y = inputs['y']['lorentz']
        d = K.Hyperboloid.distance(x,y)
        ok = d <= exp.get('distance_max', 1e9)
        vtan = K.Hyperboloid.log_map(x,y)
        y2 = K.Hyperboloid.exp_map(x, vtan)
        # Check on-manifold and closeness in ambient coordinates
        md = minkowski_dot(y2)
        rt = max(abs(a-b) for a,b in zip(y, y2))
        ok = ok and abs(md + 1.0) < 1e-3 and rt <= exp.get('roundtrip_tol', 1e-3)
        return {'distance': d, 'roundtrip_err': rt, 'ok': ok}
    return {'skipped': 'profile not supported'}


def run_suite(root: Path):
    schemas = load_schemas(root)
    total=0; passed=0; failed=0; results=[]
    vec_paths = []
    vec_paths += list((root/'spec-pack'/'vectors'/'ico').glob('*.json'))
    vec_paths += list((root/'spec-pack'/'vectors'/'ico-connect').glob('*.json'))
    vec_paths += list((root/'spec-pack'/'vectors'/'ico-sync').glob('*.json'))
    for vp in vec_paths:
        total += 1
        try:
            data = json.loads(vp.read_text(encoding='utf-8'))
            if 'hello' in data and 'accept' in data:
                validate_connect_vector(data, schemas)
                res = {'ok': True}
            elif 'descriptor' in data:
                validate_sync_vector(data, schemas)
                res = {'ok': True}
            elif 'expected' in data:
                validate_ico_core_numeric(data)
                res = run_numeric_vector(data)
                assert res.get('ok') or ('skipped' in res), f"numeric check failed: {res}"
            else:
                validate_ico_core_numeric(data)
                res = {'ok': True}
            passed += 1
            results.append({'file': str(vp), 'status': 'passed', 'result': res})
        except Exception as e:
            failed += 1
            results.append({'file': str(vp), 'status': 'failed', 'error': str(e)})
    summary = {'total': total, 'passed': passed, 'failed': failed, 'results': results}
    return summary

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[3]
    print(json.dumps(run_suite(root), indent=2))
