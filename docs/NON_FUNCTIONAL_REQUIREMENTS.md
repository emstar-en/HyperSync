# Non-Functional Requirements (NFRs)

## 1. Performance
-   **Latency**: Local consensus (Tier 1) must complete in < 10ms.
-   **Throughput**: The Geometry Engine must process 100,000 state transitions per second per core.
-   **Jitter**: Deterministic execution requires < 1ms jitter in loop timing.

## 2. Reliability
-   **Availability**: 99.99% uptime for the Consensus Layer.
-   **Durability**: Zero data loss on committed state (RPO = 0).
-   **Recovery**: Cold start to full sync in < 5 seconds.

## 3. Security
-   **Zero Trust**: All inter-agent communication must be mutually authenticated (mTLS).
-   **Post-Quantum**: All cryptographic proofs must be quantum-resistant (or have a migration path).
-   **Isolation**: Tenant data must be mathematically separated (distance > $\infty$ effectively).

## 4. Observability
-   **Transparency**: 100% of state transitions must be logged with a receipt.
-   **Visualizability**: The entire system state must be renderable in 2D/3D in real-time.
