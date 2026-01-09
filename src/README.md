# HyperSync Implementation Guide

## Overview
This directory contains the reference implementation of the HyperSync protocol.

## Getting Started

### Prerequisites
- Python 3.9+
- Linux/MacOS environment

### Installation
1. Run the deployment script:
   ```bash
   ./utilities/deployment/deploy.sh
   ```

### Directory Structure
- `api/`: FastAPI routers and endpoints.
- `core/`: Core logic (Geometry, Consensus).
- `utilities/`: Helper scripts and configs.
- `agents/`: Agent implementations.

## Development
To run tests:
```bash
pytest tests/
```
