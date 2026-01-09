# Thermodynamic Logic & Algorithms

## Overview
This document specifies the exact algorithms for implementing **Information Thermodynamics** and **Acceptance Gates** within the HyperSync Core. STUNIR must implement these functions in the `core.physics` module.

## 1. Signal Decay (Hyperbolic Attenuation)

**Function:** `calculate_signal_strength(initial_energy, distance, decay_constant)`

**Logic:**
Information propagates through the Poincaré disk. As distance ($d$) increases, signal strength ($S$) decays exponentially.

$$ S = E_0 \cdot e^{-\lambda \cdot d} $$

**Python Implementation Spec:**
```python
import math

def calculate_signal_strength(initial_energy: float, distance: float, decay_lambda: float = 1.0) -> float:
    """
    Calculates the attenuated signal strength based on hyperbolic distance.

    Args:
        initial_energy (float): The raw confidence/importance score (0.0 to 1.0).
        distance (float): The Poincaré distance between Source and Target.
        decay_lambda (float): The medium's resistance constant.

    Returns:
        float: The received signal strength.
    """
    # Clamp energy to [0, 1]
    E_0 = max(0.0, min(1.0, initial_energy))

    # Calculate decay factor
    decay_factor = math.exp(-decay_lambda * distance)

    return E_0 * decay_factor
```

## 2. Metropolis-Hastings Acceptance Gate

**Function:** `evaluate_gate(signal_strength, threshold, temperature)`

**Logic:**
Determines if a signal is "accepted" into the context window.
- If $S > 	ext{Threshold}$, accept (Deterministic).
- If $S < 	ext{Threshold}$, accept with probability $P$ (Stochastic).

$$ P = e^{-rac{\Delta E}{T}} $$
Where $\Delta E = 	ext{Threshold} - S$.

**Python Implementation Spec:**
```python
import math
import random

def evaluate_gate(signal_strength: float, threshold: float, temperature: float) -> bool:
    """
    Determines if a signal passes the thermodynamic gate.

    Args:
        signal_strength (float): The received signal energy.
        threshold (float): The minimum energy required for deterministic acceptance.
        temperature (float): The system temperature (T). Higher T = more permissive.

    Returns:
        bool: True if accepted, False if rejected.
    """
    # 1. Deterministic Check
    if signal_strength >= threshold:
        return True

    # 2. Zero Temperature Check (Strict Mode)
    if temperature <= 1e-6:
        return False

    # 3. Stochastic Check (Boltzmann)
    delta_E = threshold - signal_strength
    probability = math.exp(-delta_E / temperature)

    return random.random() < probability
```

## 3. Integration
These functions must be called by the `Agent.receive_message()` method in the `core.agents` module.
