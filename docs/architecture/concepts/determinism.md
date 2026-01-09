# HyperSync Determinism

## Determinism Guarantee

HyperSync guarantees deterministic execution: **same inputs always produce same outputs**.

## Sources of Non-Determinism (Eliminated)

### 1. Random Number Generation
- **Problem**: Random numbers are non-deterministic
- **Solution**: Use fixed seeds or deterministic PRNGs
- **Verification**: Re-execution produces same "random" sequence

### 2. System Time
- **Problem**: System time varies between executions
- **Solution**: Use epoch timestamps (fixed at build time)
- **Verification**: Time is constant across executions

### 3. Concurrency
- **Problem**: Thread scheduling is non-deterministic
- **Solution**: Deterministic scheduling or commutative operations
- **Verification**: Parallel execution produces same result

### 4. External State
- **Problem**: External systems may change
- **Solution**: Snapshot external state or avoid dependencies
- **Verification**: Execution independent of external state

### 5. Floating Point
- **Problem**: Floating point operations may vary by platform
- **Solution**: Use fixed-precision arithmetic or exact representations
- **Verification**: Bit-identical results across platforms

## Determinism Verification

### Receipt-Based Verification
```
1. Execute operation
2. Generate receipt with output checksum
3. Re-execute operation
4. Compare checksums
5. If match: deterministic ✓
6. If differ: non-deterministic ✗
```

### Continuous Verification
- Random re-execution of operations
- Checksum comparison
- Alert on non-determinism
- Root cause analysis

## STUNIR and Determinism

STUNIR (Standardization Theorem Unique Normal Intermediate Reference) ensures:
- **Unique Normal Form**: Each spec has exactly one IR representation
- **Deterministic Transformation**: Spec → IR is deterministic
- **Verifiable**: Receipts prove determinism

### Transformation Verification
```
1. Parse spec file
2. Generate STUNIR IR
3. Compute IR checksum
4. Store in receipt
5. Re-generate IR
6. Compare checksums
7. Verify determinism
```

## Determinism in Practice

### Code Generation
- Same spec → same generated code
- Template expansion is deterministic
- No timestamps in generated code (use epoch)

### Operator Execution
- Same inputs → same outputs
- No side effects except explicit ones
- All side effects logged in receipts

### Policy Evaluation
- Same state → same policy decision
- No randomness in policy logic
- All decisions logged and reproducible

## Non-Determinism Handling

When non-determinism is unavoidable:
1. **Explicit Declaration**: Declare non-deterministic operations
2. **Capture State**: Capture all inputs including "random" state
3. **Receipt Recording**: Record actual values in receipt
4. **Replay**: Use recorded values for replay/verification

## Benefits of Determinism

- **Reproducibility**: Builds and executions are reproducible
- **Debugging**: Bugs are reproducible
- **Verification**: Outputs can be verified
- **Trust**: Users can verify system behavior
- **Auditing**: Complete audit trail possible


## Determinism Tiers
For specific tier definitions (D0, D1, D2), see [Determinism Tiers](../../03_specifications/core/determinism_tiers.json).
## AGUA Enforcement

The **Automated Geometric Universal Architecture (AGUA)** is the runtime component responsible for enforcing these determinism guarantees.

AGUA intercepts all execution requests and:
1.  **Validates** the requested Determinism Tier (D0, D1, D2).
2.  **Configures** the runtime environment (e.g., setting random seeds, floating-point modes).
3.  **Verifies** outputs against recorded receipts.

For more details on the engine itself, see [AGUA Architecture](../architecture/agua.md).
