# Telemetry Capsule

This capsule provides the core telemetry functionality for HyperSync.

## Features

- **Multi-backend Support**: Export telemetry to Prometheus, Grafana, Datadog, CloudWatch, or Stdout.
- **Event Streaming**: Emit structured events with metadata.
- **Metrics Aggregation**: Record and aggregate metrics with labels.
- **Receipt Generation**: (Planned) Generate cryptographic receipts for telemetry events.

## Usage

Configure the `backends` list in the capsule configuration to enable specific exporters.