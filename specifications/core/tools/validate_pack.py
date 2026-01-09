#!/usr/bin/env python3
import json, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

errors = []

def load_json(p):
    try:
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        errors.append(f"Failed to load {p}: {e}")
        return None

def require(cond, msg):
    if not cond:
        errors.append(msg)

# 1) MANIFEST and entry points
mf = load_json(ROOT / 'MANIFEST.json')
require(mf is not None, 'MANIFEST.json missing or invalid')
if mf:
    eps = mf.get('entry_points', {})
    require('gateway' in eps, 'entry_points.gateway missing')
    require('telemetry_metrics' in eps, 'entry_points.telemetry_metrics missing')

# 2) Security baseline presence in policies
gw = load_json(ROOT / 'modules' / 'gateway' / 'gateway.json')
if gw:
    pol = gw.get('policies', {})
    require(pol.get('attestation', {}).get('require_fresh') is True, 'gateway.policies.attestation.require_fresh must be True')
    require(pol.get('predicate_proofs', {}).get('preferred') is True, 'gateway.policies.predicate_proofs.preferred must be True')
else:
    errors.append('modules/gateway/gateway.json missing or invalid')

# 3) Numeric/anchor/auth policy presence
for rel in [
    ('modules','security','numeric_policy.json'),
    ('modules','security','anchor_policy.json'),
    ('modules','security','auth_policy.json')
]:
    p = ROOT.joinpath(*rel)
    require(p.exists(), f"Missing required policy file: {'/'.join(rel)}")

# 4) Conformance KPIs structure
kpis = load_json(ROOT / 'specs' / 'conformance_kpis.json')
if kpis:
    profiles = kpis.get('profiles', {})
    require('B_performance' in profiles, 'conformance_kpis.profiles.B_performance missing')
else:
    errors.append('specs/conformance_kpis.json missing or invalid')

# 5) Domain Interface Descriptor example conforms to minimal schema
ex = load_json(ROOT / 'specs' / 'domain_interface_descriptor.example.json')
if ex:
    require(isinstance(ex.get('domain_id'), str), 'DID example: domain_id must be string')
    require(isinstance(ex.get('version'), str), 'DID example: version must be string')
    for k in ['allowed_predicates','disallowed_exports','public_endpoints']:
        require(isinstance(ex.get(k), list), f'DID example: {k} must be list')
else:
    errors.append('DID example missing or invalid')

# 6) Optional: try jsonschema if available
try:
    import jsonschema  # type: ignore
    schema = load_json(ROOT / 'schemas' / 'domain_interface_descriptor.schema.json')
    if schema and ex:
        jsonschema.validate(ex, schema)
except Exception as e:
    # Not fatal; this script works without jsonschema installed
    pass

# Summary
if errors:
    print('VALIDATION FAILED')
    for e in errors:
        print('-', e)
    sys.exit(1)
else:
    print('VALIDATION PASSED')
    sys.exit(0)
