"""
HyperSync TUI Health Check

Health check endpoint for monitoring.
"""

import logging
from typing import Dict, Any
from datetime import datetime


logger = logging.getLogger(__name__)


class HealthCheck:
    """
    Health check.

    Provides health status for monitoring systems.
    """

    def __init__(self):
        self.start_time = datetime.utcnow()
        self.checks: Dict[str, bool] = {}
        logger.info("HealthCheck initialized")

    def register_check(self, name: str, check_fn):
        """Register health check."""
        self.checks[name] = check_fn

    def get_status(self) -> Dict[str, Any]:
        """Get health status."""
        status = {
            "status": "healthy",
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "checks": {}
        }

        for name, check_fn in self.checks.items():
            try:
                result = check_fn()
                status["checks"][name] = {"status": "pass" if result else "fail"}
            except Exception as e:
                status["checks"][name] = {"status": "fail", "error": str(e)}
                status["status"] = "degraded"

        return status


# Global health check
_health_check = None


def get_health_check() -> HealthCheck:
    """Get global health check."""
    global _health_check
    if _health_check is None:
        _health_check = HealthCheck()
    return _health_check
