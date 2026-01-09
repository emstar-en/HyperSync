# Initialization Assistant Model – Bootstrap Flow

This document describes the canonical first-run bootstrap flow implemented
by the Initialization Assistant Model (IAM).

The goal is to make first-run behavior **predictable**, **testable**, and
**easy to implement** across different runtime targets.

## Scope

This flow assumes:

- A local runtime (no hard dependency on cloud services).
- A hardware probe capable of emitting a `hardware_profile` document.
- Access to NVM, SDL, and VNES surfaces as described in the core
  HyperSync specifications.

## Happy-Path State Machine

The canonical happy-path for IAM during first-run consists of the
following states:

1. **DETECT_ENVIRONMENT**
   - Inputs: raw OS/hardware/environment signals.
   - Outputs: environment snapshot, candidate probes.
   - Notes: may reuse host-provided probes when available.

2. **LOAD_OR_CREATE_HARDWARE_PROFILE**
   - Inputs: environment snapshot, hardware probe.
   - Outputs: `hardware_profile` document conforming to
     `03_specifications/environment/hardware_profile.schema.json`.
   - Receipts: MAY emit diagnostic receipts if probe fails or is
     degraded.

3. **INITIALIZE_CORE_NVM_BLOCKS**
   - Inputs: `hardware_profile`.
   - Outputs: NVM blocks for system docs, user workspace, and system
     experience.
   - Notes: must respect constraints declared in the `hardware_profile`
     (e.g. `no_persistent_logs`).

4. **SDL_DISCOVERY**
   - Inputs: `hardware_profile`, initial configuration intent.
   - Outputs: SDL shard matches (e.g. small-device, offline-friendly).
   - Receipts: SHOULD emit `sdl_query_receipt` objects conforming to
     `03_specifications/sdl/sdl_query_receipt.schema.json`.

5. **VNES_SELECTION**
   - Inputs: SDL discovery results, governance/policy capsules.
   - Outputs: list of recommended extension profiles and bundles.
   - Notes: must respect determinism tiers and any constraints derived
     from the `hardware_profile`.

6. **BOOTSTRAP_DIALOG**
   - Inputs: VNES recommendations, quick-start patterns, docs.
   - Outputs: user- or operator-facing choices and confirmations.
   - Notes: typically rendered as a short, focused first-run dialogue
     (see `examples/iam/iam_first_run_ultra_light_script.json`).

7. **APPLY_PROFILE_AND_INITIALIZE**
   - Inputs: user/operator choices, selected bundles.
   - Outputs: concrete runtime configuration (enabled operators,
     capsules, and policies), NVM updates.

8. **EMIT_BOOTSTRAP_RECEIPTS**
   - Inputs: full history of states and decisions.
   - Outputs: bootstrap receipt conforming to
     `03_specifications/environment/bootstrap_receipt.schema.json` and
     any related diagnostic receipts.

9. **READY_FOR_USER**
   - Inputs: finalized configuration.
   - Outputs: IAM hands control to the steady-state runtime / assistant
     surfaces.

## Minimal Implementation Checklist

A minimal IAM implementation SHOULD be able to:

- Produce or obtain a `hardware_profile` document and validate it.
- Create the required NVM blocks for first-run.
- Issue at least one SDL query and record a query receipt.
- Request at least one recommendation pass from VNES.
- Render a short, clear first-run dialogue that:
  - Explains what is being configured.
  - Offers a small number of sensible defaults.
- Emit a bootstrap receipt capturing the overall outcome.

For deeper integration details, see:

- `07_documentation/first_run_nvm_bootstrap.md`
- `07_documentation/human/reference/iam.md`
