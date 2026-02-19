# HyperSync Core Tier Promotions

**Document Version:** 1.0  
**Date:** 2026-01-15  
**Status:** PROPOSED

---

## Executive Summary

After comprehensive analysis of all Basic tier specifications (Phases 7A-7E), this document identifies **75 operations** that should be promoted to Core tier based on their fundamental importance to HyperSync's hyperbolic/geometric computing capabilities.

---

## Core Tier Criteria

Operations promoted to Core tier must meet one or more of these criteria:

1. **Foundational** - Operations without which HyperSync cannot function
2. **Geometric Primitives** - Low-level geometric computations that other operations depend on
3. **Hyperbolic Fundamentals** - Core hyperbolic geometry operations
4. **Curvature Essential** - Ricci curvature and flow operations central to manifold computing

---

## Promotion Recommendations

### 1. Linear Algebra Fundamentals (~20 operations)
**Source:** Phase 7B-1 (math/linear_algebra/)

| Operation | Source File | Justification |
|-----------|-------------|---------------|
| `vector_create` | vector_operations_spec.json | Foundation for all point/direction representations |
| `vector_dot_product` | vector_operations_spec.json | Essential for metric computations |
| `vector_cross_product` | vector_operations_spec.json | Required for normal/tangent calculations |
| `vector_normalize` | vector_operations_spec.json | Unit vectors essential for geodesics |
| `vector_norm` | vector_operations_spec.json | Distance/magnitude fundamental |
| `matrix_create` | matrix_operations_spec.json | Foundation for transformations |
| `matrix_multiply` | matrix_operations_spec.json | Core operation for all transforms |
| `matrix_transpose` | matrix_operations_spec.json | Essential for metric tensors |
| `matrix_inverse` | matrix_operations_spec.json | Required for coordinate transforms |
| `matrix_determinant` | matrix_operations_spec.json | Volume/orientation calculations |
| `lu_decomposition` | matrix_decompositions_spec.json | Foundation for linear solvers |
| `qr_decomposition` | matrix_decompositions_spec.json | Essential for orthogonalization |
| `svd_decomposition` | matrix_decompositions_spec.json | Core for dimensionality/stability |
| `cholesky_decomposition` | matrix_decompositions_spec.json | Required for positive-definite metrics |
| `eigenvalues_compute` | eigenvalue_spec.json | Spectral analysis for curvature |
| `eigenvectors_compute` | eigenvalue_spec.json | Principal directions on manifolds |
| `solve_linear_system` | linear_systems_spec.json | Core for all numerical methods |
| `sparse_matrix_create` | special_matrices_spec.json | Large-scale manifold computations |
| `diagonal_matrix_create` | special_matrices_spec.json | Metric tensor representations |
| `identity_matrix` | special_matrices_spec.json | Foundation operation |

### 2. Geodesic Fundamentals (~25 operations)
**Source:** Phase 7C-1 (trajectory/geodesics/)

| Operation | Source File | Justification |
|-----------|-------------|---------------|
| `geodesic_distance` | geodesic_computation_spec.json | **THE** core hyperbolic distance measure |
| `geodesic_compute` | geodesic_computation_spec.json | Shortest path on manifold |
| `geodesic_point_at` | geodesic_computation_spec.json | Point along geodesic curve |
| `geodesic_tangent_at` | geodesic_computation_spec.json | Velocity vector on geodesic |
| `geodesic_parallel_transport` | geodesic_computation_spec.json | Vector transport fundamental |
| `exponential_map` | geodesic_computation_spec.json | Tangent to manifold mapping |
| `logarithmic_map` | geodesic_computation_spec.json | Manifold to tangent mapping |
| `geodesic_shooting` | geodesic_computation_spec.json | Initial value geodesic solver |
| `geodesic_interpolation` | geodesic_interpolation_spec.json | Lerp on manifolds |
| `geodesic_midpoint` | geodesic_interpolation_spec.json | Fréchet mean primitive |
| `geodesic_slerp` | geodesic_interpolation_spec.json | Spherical interpolation |
| `geodesic_mean` | geodesic_interpolation_spec.json | Riemannian centroid |
| `geodesic_flow_tangent_bundle` | geodesic_flows_spec.json | Hamiltonian dynamics |
| `hamiltonian_geodesic_flow` | geodesic_flows_spec.json | Energy-preserving flow |
| `geodesic_curvature` | geodesic_properties_spec.json | Curve deviation from geodesic |
| `geodesic_length` | geodesic_properties_spec.json | Arc length computation |
| `hyperbolic_geodesic` | multi_geometry_geodesics_spec.json | **CORE** - hyperbolic shortest path |
| `spherical_geodesic` | multi_geometry_geodesics_spec.json | Great circle computation |
| `poincare_geodesic` | multi_geometry_geodesics_spec.json | Poincaré disk model geodesic |
| `klein_geodesic` | multi_geometry_geodesics_spec.json | Klein model geodesic |
| `hyperboloid_geodesic` | multi_geometry_geodesics_spec.json | Lorentz model geodesic |
| `geodesic_boundary_conditions` | geodesic_computation_spec.json | BVP solver for geodesics |
| `christoffel_symbols` | geodesic_computation_spec.json | Connection coefficients |
| `geodesic_equation_solve` | geodesic_computation_spec.json | ODE system for geodesics |
| `geodesic_completeness_check` | geodesic_properties_spec.json | Manifold completeness test |

### 3. Ricci Curvature Fundamentals (~30 operations)
**Source:** Phase 7E (ricci_flow/)

| Operation | Source File | Justification |
|-----------|-------------|---------------|
| `compute_ollivier_ricci_curvature` | ricci_flow_fundamentals_spec.json | **PRIMARY** Ricci curvature for graphs |
| `compute_forman_ricci_curvature` | ricci_flow_fundamentals_spec.json | Discrete Ricci via Bochner |
| `ricci_flow_step` | ricci_flow_fundamentals_spec.json | Single iteration of Ricci flow |
| `ricci_flow_evolve` | ricci_flow_fundamentals_spec.json | Full Ricci flow evolution |
| `normalized_ricci_flow` | ricci_flow_fundamentals_spec.json | Volume-preserving flow |
| `ricci_flow_convergence` | ricci_flow_fundamentals_spec.json | Flow termination criteria |
| `ricci_soliton_detect` | ricci_flow_fundamentals_spec.json | Self-similar solution detection |
| `scalar_curvature_compute` | ricci_flow_fundamentals_spec.json | Trace of Ricci tensor |
| `ricci_tensor_compute` | ricci_flow_fundamentals_spec.json | Full Ricci tensor |
| `sectional_curvature` | ricci_flow_fundamentals_spec.json | Gaussian curvature generalization |
| `compute_graph_laplacian` | graph_curvature_operations_spec.json | **ESSENTIAL** - encodes graph structure |
| `compute_weighted_graph_laplacian` | graph_curvature_operations_spec.json | Weighted variant for metrics |
| `compute_edge_curvature_distribution` | graph_curvature_operations_spec.json | Statistical curvature analysis |
| `compute_vertex_curvature` | graph_curvature_operations_spec.json | Node-level curvature |
| `curvature_clustering` | graph_curvature_operations_spec.json | Curvature-based community detection |
| `spectral_gap_compute` | graph_curvature_operations_spec.json | Connectivity measure |
| `effective_resistance` | graph_curvature_operations_spec.json | Electrical network distance |
| `heat_kernel_signature` | graph_curvature_operations_spec.json | Multi-scale shape descriptor |
| `diffusion_distance` | graph_curvature_operations_spec.json | Random walk-based distance |
| `optimal_transport_distance` | graph_curvature_operations_spec.json | Wasserstein distance for Ollivier |
| `probability_measure_assign` | graph_curvature_operations_spec.json | Distribution for ORC |
| `ricci_flow_graph` | graph_curvature_operations_spec.json | Graph-specific Ricci flow |
| `curvature_flow_normalize` | graph_curvature_operations_spec.json | Normalization strategies |
| `bottleneck_detection` | graph_curvature_operations_spec.json | Negative curvature identification |
| `community_curvature` | graph_curvature_operations_spec.json | Inter-community curvature |
| `graph_topology_from_curvature` | graph_curvature_operations_spec.json | Topological inference |
| `curvature_homogeneity` | graph_curvature_operations_spec.json | Uniformity measure |
| `ricci_flatness_test` | graph_curvature_operations_spec.json | Zero curvature detection |
| `negative_curvature_region` | graph_curvature_operations_spec.json | Hyperbolic region identification |
| `positive_curvature_region` | graph_curvature_operations_spec.json | Spherical region identification |

---

## Estimated Operation Counts After Reorganization

| Tier | Before | After | Change |
|------|--------|-------|--------|
| Core | ~180* | ~255 | +75 |
| Basic | ~485 | ~410 | -75 |
| **Total** | ~665 | ~665 | 0 |

*Core tier count estimated from existing Core tier specifications

---

## Operations Remaining in Basic Tier

The following categories should remain in Basic tier:

### Phase 7A (General Operations) - ALL STAY BASIC
- File I/O operations (not geometric primitives)
- Network operations
- System utilities
- Data structure helpers (non-geometric)

### Phase 7B (Mathematical Extensions) - PARTIAL PROMOTION
- **Statistics:** ALL stay Basic (not geometric fundamentals)
- **Calculus:** Most stay Basic (numerical methods, not geometric core)
- **Numerical:** FFT, signal processing stay Basic

### Phase 7C (Trajectory Operations) - PARTIAL PROMOTION
- **Curves:** Bezier, splines stay Basic (convenience, not fundamental)
- **Motion:** Kinematics stay Basic (physics layer, not geometric core)

### Phase 7D (Tooling) - ALL STAY BASIC
- All development/infrastructure tools remain Basic
- Not related to geometric computing

---

## Implementation Notes

1. **No Breaking Changes:** Promoted operations maintain full API compatibility
2. **Dependency Resolution:** Core tier operations have no Basic tier dependencies
3. **Documentation:** Core tier gets enhanced mathematical documentation
4. **Testing:** Core operations require additional numerical stability tests

---

## Approval Status

- [ ] Architecture Review
- [ ] API Compatibility Check
- [ ] Documentation Update
- [ ] Test Coverage Verification

---

*Document generated by HyperSync Core Tier Analysis*
