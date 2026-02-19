# Psychometric Tensor Specification

## Overview
In HyperSync, "psychological" factors (user sentiment, agent confidence, system "stress") are not abstract metadata—they are **first-class geometric dimensions**.

## The Psychometric Tensor
We define a **Psychometric Tensor** $\Psi$ as a vector in the hyperbolic state space.

$$ \Psi = [ 	ext{valence}, 	ext{arousal}, 	ext{dominance}, 	ext{entropy}, 	ext{coherence} ] $$

### Mapping to Geometry
*   **Center (0,0)**: "Zen" / Equilibrium. Perfect clarity, neutral sentiment, zero stress.
*   **Edge (Approaching 1)**: "Panic" / Instability. Extreme emotion, high confusion, maximum stress.

## Integration with VNES
Psychological models (like `sentiment-analyzer`) are VNES Capsules that:
1.  **Input**: Text, Audio, or System Logs.
2.  **Process**: Analyze the input using ML or heuristics.
3.  **Output**: A **Psychometric Tensor** update vector $\Delta \Psi$.

### Usage in Consensus
The geometry engine treats $\Psi$ like any other physical force.
*   **High Stress (Entropy)**: Increases the "Temperature" $eta$, making Acceptance Gates stricter (system locks down to prevent errors).
*   **High Confidence (Coherence)**: Lowers the "Temperature", allowing for faster, more speculative execution.

## Example: "The Anxious Agent"
If an agent's internal state shows high entropy (confusion):
1.  Its position in the Poincaré disk drifts towards the edge.
2.  Its "Voice" (voting power) in consensus is geometrically attenuated.
3.  The system automatically routes "Therapeutic" tasks (simplification, rollback) to it to restore equilibrium.
