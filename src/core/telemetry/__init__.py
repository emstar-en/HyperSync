"""
HyperSync telemetry module.
"""

from .telemetry_manager import (
    TelemetryManager,
    TelemetryEvent,
    TelemetryBackend,
    get_telemetry_manager,
    emit_event,
    record_metric
)

__all__ = [
    'TelemetryManager',
    'TelemetryEvent',
    'TelemetryBackend',
    'get_telemetry_manager',
    'emit_event',
    'record_metric'
]
