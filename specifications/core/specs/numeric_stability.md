# Numeric Stability & Hyperbolic Arithmetic Specification

## Overview
This document defines the strict arithmetic rules required to maintain stability in the Poincaré disk model ($|z| < 1$). Hyperbolic geometry is highly sensitive to floating-point errors near the boundary of the disk.

## 1. Boundary Conditions & Clamping

### The Boundary Problem
As a point $z$ approaches the boundary $|z| = 1$, the hyperbolic distance $d(0, z)$ approaches infinity.
$$ d(0, z) = 2 	anh^{-1}(|z|) $$
Floating point errors can push a valid point onto or outside the unit circle, causing `NaN` or `Inf` in distance calculations.

### Clamping Rule
All geometric operations returning a point $z$ MUST apply the clamping function $	ext{clamp}(z)$.

**Constants:**
- `EPSILON`: $1 	imes 10^{-6}$ (Safety margin)
- `MAX_NORM`: $1.0 - 	ext{EPSILON}$ ($0.999999$)

**Function:**
$$
	ext{clamp}(z) = 
egin{cases} 
z & 	ext{if } |z| \le 	ext{MAX\_NORM} \
z \cdot rac{	ext{MAX\_NORM}}{|z|} & 	ext{if } |z| > 	ext{MAX\_NORM}
\end{cases}
$$

## 2. Möbius Addition (Gyrovector Addition)
In hyperbolic space, vectors do not add linearly. We must use Möbius addition ($\oplus$).

**Formula:**
For two complex numbers $z, w$ in the unit disk:
$$ z \oplus w = rac{z + w}{1 + ar{z}w} $$

**Implementation Notes:**
- Inputs $z, w$ must be clamped *before* addition if they come from untrusted sources.
- The result must be clamped *after* calculation.
- Denominator $1 + ar{z}w$ is never 0 for points within the unit disk.

## 3. Precision Standards
- **Data Type**: All coordinates must use 64-bit floating point numbers (`double` / `float64`).
- **Tolerance**: Equality checks must use an absolute tolerance of $1 	imes 10^{-9}$.
