# Intrinsic Fused Kernels

This document defines interfaces and behaviors for fused intrinsic kernels that minimize memory traffic
and improve numeric stability without Euclidean intermediates.

Fusions:
- fused_exp_log_retract: combines exp/log, norm checks, and retraction with curvature scaling.
- fused_transport_project: combines parallel transport and projection to manifold constraints.

Determinism:
- Kernels MUST be bitwise deterministic under the active numeric_policy.

Precision:
- Compute in bf16/fp16 when permitted; accumulate in fp32; promote on threshold triggers.
