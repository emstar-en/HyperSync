"""
HyperSync wiring module - Integration modes and system wiring.
"""

from .integration_modes import (
    IntegrationMode,
    IntegrationCapabilities,
    IntegrationProfile,
    IntegrationModeManager,
    get_mode_manager,
    set_integration_mode,
    get_integration_mode,
    has_capability
)

__all__ = [
    'IntegrationMode',
    'IntegrationCapabilities',
    'IntegrationProfile',
    'IntegrationModeManager',
    'get_mode_manager',
    'set_integration_mode',
    'get_integration_mode',
    'has_capability'
]
