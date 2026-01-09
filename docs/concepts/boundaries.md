# HyperSync Boundaries

## What HyperSync Does NOT Do

### 1. General-Purpose Computing
HyperSync is NOT a general-purpose programming language or runtime. It is specifically designed for:
- Orchestration of distributed workloads
- Geometric computation in hyperbolic space
- Deterministic workflow execution

### 2. Data Storage
HyperSync does NOT provide:
- Long-term data storage
- Database functionality
- Persistent data management

It coordinates and orchestrates, but delegates storage to external systems.

### 3. User Interface
HyperSync does NOT include:
- Built-in user interfaces
- Web dashboards
- Graphical tools

UI extensions are available separately in `11_extensions/ui/`.

### 4. Machine Learning
HyperSync does NOT:
- Train machine learning models
- Provide ML frameworks
- Include ML algorithms

It orchestrates ML workloads but does not implement ML itself.

### 5. Network Infrastructure
HyperSync does NOT:
- Manage network hardware
- Provide network routing
- Handle low-level networking

It operates at the application layer.

## Scope Boundaries

### In Scope
- Orchestration and coordination
- Hyperbolic geometry computations
- Deterministic execution
- Receipt generation and verification
- Policy enforcement
- Operator execution

### Out of Scope
- Application business logic (user-defined)
- Data persistence (delegated to external systems)
- User authentication (uses external IAM)
- Hardware management (uses container orchestration)
- Network infrastructure (uses existing networks)

## Integration Points

HyperSync integrates with external systems for:
- **Storage**: Databases, object stores, file systems
- **Authentication**: IAM systems, OAuth providers
- **Monitoring**: Prometheus, Grafana, etc.
- **Deployment**: Kubernetes, Docker, cloud platforms
- **CI/CD**: Jenkins, GitLab CI, GitHub Actions
