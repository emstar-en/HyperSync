"""
JSON formatter for CLI output
"""

import json
from typing import Any

class JSONFormatter:
    """Formats data as JSON."""

    @staticmethod
    def format(data: Any, indent: int = 2) -> str:
        """Format data as JSON string."""
        return json.dumps(data, indent=indent)

    @staticmethod
    def format_compact(data: Any) -> str:
        """Format data as compact JSON."""
        return json.dumps(data, separators=(',', ':'))
