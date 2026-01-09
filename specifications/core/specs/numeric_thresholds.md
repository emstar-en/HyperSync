# Numeric Policy Thresholds & Precision Standards

## 1. Floating Point Standards
*   **Base Precision**: IEEE 754 Binary64 (Double Precision) is the standard for all geometric state calculations.
*   **Storage Format**: Binary32 (Single Precision) is acceptable for serialized storage of non-critical historical traces, provided they are promoted to Binary64 before use.
*   **Epsilon ($\epsilon$)**:
    *   $\epsilon_{64} pprox 2.22 	imes 10^{-16}$
    *   $\epsilon_{32} pprox 1.19 	imes 10^{-7}$

## 2. Poincaré Disk Constraints
The system operates on the Poincaré disk model $\mathbb{D} = \{z \in \mathbb{C} : |z| < 1\}$.

### 2.1 Boundary Safety
To prevent numerical instability near the boundary $\partial\mathbb{D}$ (where metric tensor $g 	o \infty$), we enforce a **Safe Radius** $R_{safe}$.

*   **$R_{safe}$**: $1.0 - 10^{-12}$
*   **Clamping**: Any point $z$ resulting from an operation where $|z| \ge R_{safe}$ must be clamped:
    $$ z_{clamped} = z \cdot rac{R_{safe}}{|z|} $$
*   **Warning Threshold**: $|z| > 1.0 - 10^{-6}$ triggers a `GeometryWarning`.

### 2.2 Metric Tensor Stability
The metric is $ds^2 = rac{4|dz|^2}{(1-|z|^2)^2}$.
*   **Singularity Guard**: The denominator $(1-|z|^2)^2$ must never be effectively zero.
    *   Minimum Denominator Value: $10^{-24}$

## 3. Operation Tolerances (Acceptance Gates)

### 3.1 Möbius Transformations
For a transformation $f(z) = rac{az+b}{ar{b}z+ar{a}}$ with $|a|^2 - |b|^2 = 1$:
*   **Determinant Check**: $| (|a|^2 - |b|^2) - 1.0 | < 10^{-14}$
*   **Unitary Deviation**: For matrix representation $M$, $||M^\dagger \eta M - \eta||_F < 10^{-14}$ where $\eta = 	ext{diag}(1, -1)$.

### 3.2 Isometry Invariance
Distance $d(z_1, z_2)$ must be preserved under isometry $T$.
*   **Drift Tolerance**: $|d(T(z_1), T(z_2)) - d(z_1, z_2)| < 50 \cdot \epsilon_{64}$

### 3.3 Parallel Transport
Transporting a vector $v$ along a closed loop $\gamma$ (holonomy) should return $v$ rotated by the curvature flux.
*   **Closure Error**: For a trivial loop (contractible to point), $||v_{final} - v_{initial}|| < 10^{-12}$.

## 4. ULP Budgets (Deterministic Execution)
To ensure cross-platform determinism, operations are budgeted by Units in the Last Place (ULP).

| Operation | Max ULP Error (Double) | Max ULP Error (Single) |
| :--- | :--- | :--- |
| `hyp_dist(z1, z2)` | 4 | 16 |
| `mobius_apply(M, z)` | 2 | 8 |
| `midpoint(z1, z2)` | 4 | 16 |
| `exp_map(z, v)` | 8 | 32 |
| `log_map(z1, z2)` | 8 | 32 |

*   **Violation**: Exceeding ULP budget results in a `DeterministicViolation` error and rejects the computation block.

## 5. NaN and Infinity Handling
*   **Strict Mode**: Any `NaN` or `Inf` detected in the geometric state vector immediately halts the consensus round (`StateCorruptionError`).
*   **Sanitization**: Inputs from external agents must be sanitized (checked for `NaN`/`Inf`) before entering the Geometry Engine.

## 6. Denormalized Numbers
*   **Policy**: Flush-to-zero (FTZ) and Denormals-are-zero (DAZ) are **DISABLED** for Geometry Engine. Subnormal precision is required for accurate boundary calculations.
*   **Exception**: FTZ is permitted in the *Rendering/Visualization* pipeline only.
