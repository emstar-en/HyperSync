# Deployment Documentation Generation Policy

This document outlines the policy for generating deployment documentation for HyperSync.

## Philosophy

Deployment documentation is not written by hand. It is generated deterministically from the `machine-optimized` build artifacts produced by STUNIR. This ensures that the documentation always matches the code being deployed.

## Policy

The generation policy is defined in `deployment_docs.spec.json`.

### Source of Truth

The source of truth for all deployment documentation is the `artifact://stunir/machine_optimized` stream.

### Targets

We currently support the following deployment targets:

*   **AWS**: via Terraform
*   **Kubernetes**: via Helm
*   **Bare Metal**: via Ansible

### Validation

All generated documentation must pass the following validation rules:

1.  **Parameter Parity**: Every configurable parameter in the deployment artifact must be documented.
2.  **Version Alignment**: The version in the docs must match the version in the artifact.
3.  **Security Context**: Security contexts and permissions must be explicitly documented.
