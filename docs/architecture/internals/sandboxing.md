# HyperSync Sandbox Specification

## Overview
The HyperSync Sandbox is a restricted execution environment designed to safely run "Yellow Lane" (Zone 2) capsules. These capsules are untrusted, unverified, or experimental code that must be prevented from compromising the host system or the global consensus state.

## Isolation Strategy
HyperSync employs a **"Defense in Depth"** strategy for sandboxing, utilizing multiple layers of isolation depending on the host OS capabilities.

### Layer 1: Language-Level Isolation (Python Restricted Execution)
- **Mechanism:** Custom `exec()` environment with a restricted `__builtins__`.
- **Restrictions:**
    - No `import os`, `import sys`, `import subprocess`.
    - No file I/O (`open`, `write`).
    - No network sockets.
    - Access only to whitelisted HyperSync APIs (e.g., `ctx.log()`, `ctx.read_state()`).

### Layer 2: Resource Limits (cgroups / ulimit)
- **CPU:** Hard cap on CPU shares (e.g., 10% of a core).
- **Memory:** Hard limit on RAM usage (e.g., 128MB).
- **Processes:** Max process count = 1 (no forking).

### Layer 3: Filesystem Jail (chroot / namespace)
- **Root:** The capsule sees a minimal, read-only filesystem.
- **Temp:** A private, ephemeral `/tmp` directory is mounted for scratch space.
- **Network:** Network namespace is completely unconfigured (no loopback, no eth0) unless explicitly whitelisted.

## Sandbox Lifecycle

1.  **Provisioning:**
    - Coordinator receives a `spawn_worker` request for a Yellow Lane capsule.
    - Coordinator allocates a unique `sandbox_id`.
    - A temporary directory is created for the capsule's runtime.

2.  **Injection:**
    - The capsule's code (from the manifest) is written to `main.py` inside the jail.
    - Configuration is injected via environment variables.

3.  **Execution:**
    - The runtime wrapper launches the process.
    - `stdout`/`stderr` are captured and piped to the Coordinator's telemetry stream.

4.  **Termination:**
    - **Voluntary:** Capsule exits with code 0.
    - **Violation:** Capsule attempts a forbidden syscall -> SIGKILL.
    - **Timeout:** Capsule exceeds execution time limit -> SIGTERM.

## Configuration Schema
See `03_specifications/schemas/runtime/sandbox_policy.schema.json` for the configuration structure.
