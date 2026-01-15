# HyperSync

A geometric computing framework for distributed systems, consensus mechanisms, and machine learning.

## Overview

HyperSync is a geometric computing framework built on non-Euclidean geometry (hyperbolic and spherical spaces) and general relativity. It provides operations for:

- **Geometric operations**: Hyperbolic and spherical geometry, exponential/logarithmic maps, parallel transport
- **Consensus mechanisms**: Byzantine fault-tolerant consensus using geometric properties
- **Security modules**: Geometric encryption, authentication, and adversarial detection
- **Black hole geometries**: Schwarzschild and Kerr black hole physics
- **Edge case handling**: Scott encoding and lambda calculus operations

## Core Tier

**Status: 357/357 operations complete (100%)** ✅

The Core Tier includes 9 major components:

1. **Dual Model System** (167 operations): Lorentz and Poincaré hyperbolic models with automatic model selection
2. **Edge Case Handling** (18 operations): Scott encoding and lambda calculus for robust corner case handling
3. **Small Components** (6 operations): Adversarial sinks, cosmological spaces, geometric BFT
4. **Spherical Geometry** (26 operations): Complete spherical geometry operations
5. **Schwarzschild Black Holes** (32 operations): Non-rotating black hole physics
6. **Kerr Black Holes** (33 operations): Rotating black hole physics with frame dragging
7. **Enhanced Exponential Maps** (33 operations): Multi-dimensional, batch processing, gradients, stability
8. **Enhanced Logarithmic Maps** (33 operations): Inverse exponential maps with cross-curvature support
9. **Enhanced Parallel Transport** (10 operations): Vector transport along geodesics

### Key Features

- **Geometric operations**: 28 core operations for hyperbolic and spherical geometry
- **Consensus mechanisms**: 5 algorithms including Raft, Paxos, Spherical BFT, Poincaré Voting, and Sampling Consensus
- **Security modules**: 6 modules including hyperbolic encryption, curvature authentication, and proximity adversarial detection
- **Heuristic methods**: 4 fast approximation algorithms for Ricci flow and curvature estimation
- **Black hole physics**: 65 operations for Schwarzschild and Kerr geometries
- **Advanced manifold operations**: 76 operations for exponential/logarithmic maps and parallel transport

## Latest Changes

### Phase 6B Complete (January 2026)
- **Enhanced Logarithmic Maps** (33 operations): Multi-dimensional log maps, batch processing, gradients, numerical stability, cross-curvature operations
- **Enhanced Parallel Transport** (10 operations): Geodesic transport, Schild's ladder, Pole ladder, holonomy computation, tensor field transport
- **Core Tier 100% Complete**: All 357 operations now fully specified with comprehensive documentation

### Phase 6A Complete (December 2025)
- **Enhanced Exponential Maps** (33 operations): Multi-dimensional exp maps, batch processing (vectorized/parallel/GPU/distributed), automatic differentiation, numerical stability, cross-curvature operations

### Phase 5B Complete (November 2025)
- **Kerr Black Hole Geometries** (26 operations): Rotating black holes with frame dragging, ergosphere, energy extraction (Penrose process, Blandford-Znajek), gravitational lensing

### Phase 5A Complete (November 2025)
- **Schwarzschild Black Hole Geometries** (24 operations): Event horizons, geodesics, physical effects, coordinate transformations, orbital mechanics, gravitational lensing, thermodynamics

### Phase 4 Complete (October 2025)
- **Small Components** (6 operations): Adversarial sinks, cosmological spaces, geometric BFT advanced
- **Spherical Geometry Verification**: All 26 core tier spherical operations verified complete

## Installation

```bash
# Clone the repository
git clone https://github.com/emstar-en/HyperSync.git
cd HyperSync

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

## Quick Start

### Hyperbolic Geometry

```python
import numpy as np
from hypersync_core.geometry import hyperbolic_distance, hyperbolic_exp_map

# Two points in Poincaré ball
x = np.array([0.1, 0.2, 0.3])
y = np.array([0.4, 0.1, 0.2])

# Compute hyperbolic distance
distance = hyperbolic_distance(x, y)
print(f"Hyperbolic distance: {distance:.4f}")

# Exponential map
v = np.array([0.1, 0.0, 0.0])  # Tangent vector
z = hyperbolic_exp_map(x, v)
print(f"Point on geodesic: {z}")
```

### Spherical BFT Consensus

```python
from hypersync_core.consensus import spherical_bft_consensus

# Node proposals (with Byzantine nodes)
proposals = [
    np.array([1.0, 0.1, 0.0]),  # Honest
    np.array([1.1, 0.0, 0.1]),  # Honest
    np.array([0.9, 0.1, 0.1]),  # Honest
    np.array([5.0, 5.0, 5.0]),  # Byzantine (outlier)
]

# Run consensus
consensus, byzantine_nodes = spherical_bft_consensus(proposals)
print(f"Consensus: {consensus}")
print(f"Byzantine nodes: {byzantine_nodes}")  # [3]
```

### Hyperbolic Encryption

```python
from hypersync_core.security import hyperbolic_encrypt, hyperbolic_decrypt

# Encrypt data
data = np.array([1.0, 2.0, 3.0])
key = b"my_secret_key_256_bits_long_____"

encrypted, nonce = hyperbolic_encrypt(data, key)
print(f"Encrypted: {encrypted}")

# Decrypt
decrypted = hyperbolic_decrypt(encrypted, nonce, key)
print(f"Decrypted: {decrypted}")
```

## Documentation

- **[API Reference](docs/API.md)** - Complete API documentation
- **[Getting Started](docs/GETTING_STARTED.md)** - Tutorial and examples
- **[Core Tier Operations](docs/CORE_TIER_OPERATIONS.md)** - Detailed operation specifications
- **[Specifications](specs/)** - JSON specifications for all operations

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/test_geometry.py
pytest tests/test_consensus.py
pytest tests/test_security.py

# Run with coverage
pytest --cov=hypersync_core tests/
```

## License

HyperSync Core tier is dual-licensed:

- **AGPLv3** for open-source use - See [LICENSE](LICENSE)
- **Commercial License** for proprietary use - See [LICENSING.md](LICENSING.md)

For commercial licensing inquiries, please see [LICENSING.md](LICENSING.md).

## Links

- **Repository**: [https://github.com/emstar-en/HyperSync](https://github.com/emstar-en/HyperSync)
- **Documentation**: [docs/](docs/)
- **Issues**: [https://github.com/emstar-en/HyperSync/issues](https://github.com/emstar-en/HyperSync/issues)

## Status

**ALPHA**: This software is in active development. APIs may change.

**Patent Pending**: Some methods and algorithms are patent pending.

---

**Made with ❤️ by the HyperSync Team**
