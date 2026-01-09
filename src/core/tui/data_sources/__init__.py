"""
HyperSync TUI Data Sources

Adapters for connecting telemetry feeds to TUI panels.
"""

import logging
from typing import Dict, Any, Optional, Callable
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class DataAdapter(ABC):
    """Base data adapter."""

    def __init__(self, channel_name: str):
        self.channel_name = channel_name
        self.subscribers: list = []

    @abstractmethod
    async def fetch(self) -> Any:
        """Fetch data from source."""
        pass

    def subscribe(self, callback: Callable):
        """Subscribe to data updates."""
        self.subscribers.append(callback)

    async def notify_subscribers(self, data: Any):
        """Notify subscribers of new data."""
        for callback in self.subscribers:
            try:
                await callback(data)
            except Exception as e:
                logger.error(f"Error in subscriber callback: {e}")
