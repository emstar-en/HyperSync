# ICO: Intrinsic Curvature Oriented Substrate — Core Specification v1.0 (Draft)

Status
- Draft specification of ICO, the geometry substrate used by HyperSync.
- Licensing: Spec CC BY 4.0; reference implementations Apache-2.0.
- Normative terms as per RFC 2119.

Visual and Naming Reference
- The letters “ICO” are a mnemonic for the three canonical geometries:
 - I — Euclidean (κ = 0), straight and flat.
 - C — Hyperbolic (κ < 0), curvature reference: open/negative.
 - O — Spherical (κ > 0), curvature reference: closed/positive.
- Profiles: ICO-E (Euclidean), ICO-H (Hyperbolic), ICO-S (Spherical).

1. Introduction and Scope
ICO defines a geometry-native substrate spanning Euclidean, hyperbolic, and spherical spaces. It standardizes:
- Types and encodings for geometry-native data.
- Core operations (distance, exp/log, parallel transport, barycenters).
- Safety contracts (“stay-on-manifold”, “no-Euclidean-intermediates” under native geometry).
- Conformance tiers and test vectors.
Non-goals: ICO is not an app protocol or storage layer; it is the substrate for higher orchestration (e.g., HyperSync).

2. Terminology and Notation
- κ: curvature. 0 for E, <0 for H, >0 for S.
- M: manifold; g: metric; T_xM: tangent space at x.
- exp/log, parallel transport (PT) carry their standard differential-geometric meanings.
- Models for H: lorentz (canonical), poincare_ball, half_space.
- IDs: ALG-ICO-xxxx, POL-ICO-xxxx, TV-ICO-xxxx.

3. Mathematical Model
3.1 Manifolds and metrics
- ICO-E: ℝ^n, metric g = I.
- ICO-H: Unit hyperboloid H^n (Lorentz model). Minkowski inner product; time-like component > 0.
- ICO-S: Unit n-sphere S^n ⊂ ℝ^{n+1}; geodesics are great circles; cut locus at antipodes.

3.2 Maps and geodesics
- exp_x: T_xM → M; log_x: M\CutLocus → T_xM; PT_{x→y}: T_xM → T_yM. All MUST be defined per profile with documented domains and numerical envelopes.

3.3 Curvature-constrained ops
- Fréchet barycenter MUST respect manifold constraints and document convergence guarantees (max_iters, tol).
- Retractions MAY be provided but MUST be flagged non-native unless equivalent to exp for the profile.

4. Data Types and Encodings
4.1 Core Types
- Point, TangentVector, Metric, Connection (implicit Levi-Civita unless stated), Distribution (optional), Payload (for orchestration layers).

4.2 Canonical JSON envelope (normative)
```json
{
 "ico_profile": "E|H|S",
 "dimension": 3,
 "model": "lorentz|poincare_ball|half_space|null",
 "curvature": 0.0,
 "normalization": {"radius": 1.0},
 "data": { }
}
```
- S: points MUST be unit norm in ambient encoding.
- H (Lorentz): points MUST satisfy ⟨x,x⟩_M = −1 and x0 > 0.
- E: ℝ^n vector points with no additional manifold constraint.

4.3 Schemas
- icod.schema.json — ICO Descriptor (capabilities, models, ops, policies).
- icov.schema.json — Test vectors and invariants.
- icop.schema.json — Numeric and determinism policies.

5. Operations and Contracts
5.1 Required (Tier 1)
- distance(x,y): metric-consistent.
- exp_map(x,v): returns point on manifold; rejects or clamps out-of-domain per policy.
- log_map(x,y): stabilized within injectivity radius; MUST document failure near cut loci (S) or spacelike regions (H).
- parallel_transport(x,y,v): preserves inner product under g.
- barycenter({w_i, x_i}): stays on M; convergence policy documented.

5.2 Recommended (Tier 2)
- model_transform_H(src_model, dst_model, x): preserves geodesic distances within tolerance.
- projection_S_ambient(x): enforce unit-norm on S^n.
- curvature_aware_gradient_step(f, x, policy): documented bounds, exp vs retraction semantics.

5.3 Safety contracts
- Stay-on-manifold: outputs MUST lie on M within tolerance.
- No-Euclidean-intermediates: when geometry_mode = native, core ops MUST NOT Euclideanize (diagnostic “approx” backdoors require explicit policy).
- Determinism: when true, identical inputs/policy MUST reproduce outputs.
- Numeric envelopes: policy MUST state max_iters, tol, retraction_strategy, conditioning thresholds.

6. Policy and Security
- POL-ICO-NUMERIC: numeric policy
 - max_iters, tol, retraction_strategy: native|approx, conditioning_guard, deterministic.
- POL-ICO-ATTEST: optional signing/provenance of descriptors and vector packs.
- Adversarial handling: reject out-of-domain inputs; safe-failure semantics required.

7. Conformance and Test Vectors
- Tier 0: encodings and schemas.
- Tier 1: distance, exp/log, PT, barycenter per profile.
- Tier 2: H model transforms; curvature-aware optimization sanity tests.
- Tier 3: composition invariants and performance envelopes (optional).
Vectors (icov) include: test_id, profile, model, inputs, expected_output (ranges, predicates), invariants (stay_on_manifold, PT-preserve-IP, exp-log_roundtrip).

8. Interoperability and Versioning
- icod example:
```json
{
 "ico_profile": ["E","H","S"],
 "dimension": 3,
 "models_supported": ["lorentz","poincare_ball"],
 "ops": ["distance","exp_map","log_map","parallel_transport","barycenter","model_transform_H"],
 "determinism": true,
 "numeric_policy": {"max_iters": 200, "tol": 1e-8, "retraction_strategy": "native"},
 "version": "1.0"
}
```
- Versioning: 1.0 Core. Deprecations via alias_of; JSON schema backward compatibility for minor versions.

9. Reference Algorithms (Informative, Normative Targets in Tests)
- ALG-ICO-DIST-E/H/S
- ALG-ICO-EXP/LOG-E/H/S
- ALG-ICO-PT-E/H/S
- ALG-ICO-BARY-E/H/S
- ALG-ICO-MODEL-XFORM-H

10. Security and Privacy
- Deterministic mode minimizes side channels; numeric policy constrains instability.
- Strict domain checks to prevent undefined behavior (antipodal S, spacelike H).

11. Governance and Licensing
- WG with ADRs, public cadence, and artifact registry for vectors.
- Spec CC BY 4.0, reference kernels Apache-2.0.

12. Profiles (Normative Appendices)
- ICO-E: ℝ^n, g=I, closed forms.
- ICO-H: Lorentz model canonical; equivalence mappings to Poincaré; stability guidance for large rapidities.
- ICO-S: S^n with great-circle geodesics; antipodal cut-locus handling.

13. Conformance Examples
- TV-ICO-001 (H distance), TV-ICO-010 (S exp/log roundtrip), TV-ICO-020 (E PT IP preservation).
