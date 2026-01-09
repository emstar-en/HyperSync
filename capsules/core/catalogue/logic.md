# Catalogue Logic

## Overview
The Catalogue manages the local "Brain Trust". It implements the schemas defined in `03_specifications/core/schemas/catalogue/`.

## Functions

### 1. Discovery
Scans the local filesystem (e.g., `/models`, `~/.cache/huggingface`) for model artifacts.
*   **Formats**: GGUF, SafeTensors, ONNX.
*   **Metadata**: Extracts parameter count, quantization level (Q4_K_M, Q8_0), and architecture.

### 2. Profiling
Runs a micro-benchmark on the host hardware (NPU/GPU/CPU) to establish a `tokens_per_second` baseline for each model.

### 3. Routing (The "Brain Router")
When the Factory asks for a "Coding Model", the Catalogue selects the best fit:
*   *Criteria*: High context window, trained on code, acceptable speed.
*   *Selection*: `codellama-7b-instruct.Q4_K_M.gguf` (Speed: 45 t/s).

When the Poker Game asks for a "Cute Dealer", the Catalogue selects:
*   *Criteria*: High creativity, roleplay ability.
*   *Selection*: `mistral-7b-openorca.Q5_K_M.gguf` (Speed: 30 t/s).
