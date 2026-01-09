"""
Configuration Manager for Domain Operations
"""

import json
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DomainConfigManager:
    """Manages configuration for domain operations"""

    DEFAULT_CONFIG = {
        "registry": {
            "enabled_domains": [
                "hyperboloid", "sphere", "flat_minkowski",
                "ads_space", "schwarzschild", "kerr",
                "frw_cosmology", "inflationary", "cyclic"
            ],
            "default_domain": "flat_minkowski",
            "auto_register": True
        },
        "routing": {
            "enable_cross_curvature": True,
            "transition_cost_model": "curvature_based",
            "max_transition_hops": 5
        },
        "policies": {
            "enforce_horizon_acl": True,
            "enforce_causality": True,
            "require_attestation": False
        },
        "capabilities": {
            "enable_time_varying": True,
            "enable_black_holes": True,
            "enable_cosmologies": True
        },
        "validation": {
            "strict_mode": False,
            "validate_on_create": True,
            "validate_transitions": True
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        self.config = self.DEFAULT_CONFIG.copy()

        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
        else:
            # Try to load from environment
            env_config = os.environ.get('HYPERSYNC_DOMAIN_CONFIG')
            if env_config and os.path.exists(env_config):
                self.load_config(env_config)

    def load_config(self, path: str) -> None:
        """Load configuration from file"""
        try:
            with open(path, 'r') as f:
                user_config = json.load(f)

            # Deep merge with defaults
            self._deep_merge(self.config, user_config)
            logger.info(f"Loaded configuration from {path}")
        except Exception as e:
            logger.error(f"Failed to load config from {path}: {e}")

    def _deep_merge(self, base: Dict, update: Dict) -> None:
        """Deep merge update into base"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated path"""
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value by dot-separated path"""
        keys = key_path.split('.')
        config = self.config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value

    def is_domain_enabled(self, domain_type: str) -> bool:
        """Check if a domain type is enabled"""
        enabled = self.get('registry.enabled_domains', [])
        return domain_type in enabled

    def is_capability_enabled(self, capability: str) -> bool:
        """Check if a capability is enabled"""
        return self.get(f'capabilities.enable_{capability}', True)

    def get_routing_config(self) -> Dict[str, Any]:
        """Get routing configuration"""
        return self.get('routing', {})

    def get_policy_config(self) -> Dict[str, Any]:
        """Get policy configuration"""
        return self.get('policies', {})

    def get_validation_config(self) -> Dict[str, Any]:
        """Get validation configuration"""
        return self.get('validation', {})

    def save_config(self, path: str) -> None:
        """Save current configuration to file"""
        try:
            with open(path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved configuration to {path}")
        except Exception as e:
            logger.error(f"Failed to save config to {path}: {e}")


# Global config manager
_global_config = None


def get_config() -> DomainConfigManager:
    """Get the global configuration manager"""
    global _global_config
    if _global_config is None:
        _global_config = DomainConfigManager()
    return _global_config


def reset_config():
    """Reset the global configuration (mainly for testing)"""
    global _global_config
    _global_config = None
