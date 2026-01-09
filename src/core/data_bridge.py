"""
Data Bridge Registry - Central adapter lifecycle manager for TUI telemetry.

Manages the lifecycle of data source adapters and routes their output
to panel state handlers.
"""
import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class AdapterState(Enum):
    """Adapter lifecycle states."""
    UNINITIALIZED = "uninitialized"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class AdapterRegistration:
    """Registration record for a data adapter."""
    adapter_id: str
    adapter_instance: Any
    state: AdapterState = AdapterState.UNINITIALIZED
    subscribers: List[Callable] = field(default_factory=list)
    poll_interval: float = 1.0  # seconds
    task: Optional[asyncio.Task] = None
    error_count: int = 0
    last_error: Optional[str] = None


class DataBridgeRegistry:
    """
    Central registry for managing data adapters and their subscribers.

    Responsibilities:
    - Register and initialize adapters
    - Manage adapter lifecycle (start, stop, restart)
    - Route adapter output to subscribers
    - Handle errors and retries
    """

    def __init__(self):
        self._adapters: Dict[str, AdapterRegistration] = {}
        self._running = False
        self._lock = asyncio.Lock()

    def register_adapter(
        self,
        adapter_id: str,
        adapter_instance: Any,
        poll_interval: float = 1.0
    ) -> None:
        """
        Register a data adapter.

        Args:
            adapter_id: Unique identifier for the adapter
            adapter_instance: The adapter instance (must have async fetch() method)
            poll_interval: How often to poll the adapter (seconds)
        """
        if adapter_id in self._adapters:
            logger.warning(f"Adapter {adapter_id} already registered, replacing")

        self._adapters[adapter_id] = AdapterRegistration(
            adapter_id=adapter_id,
            adapter_instance=adapter_instance,
            poll_interval=poll_interval
        )
        logger.info(f"Registered adapter: {adapter_id}")

    def subscribe(self, adapter_id: str, handler: Callable) -> None:
        """
        Subscribe a handler to an adapter's data stream.

        Args:
            adapter_id: The adapter to subscribe to
            handler: Async callable that receives adapter data
        """
        if adapter_id not in self._adapters:
            raise ValueError(f"Adapter {adapter_id} not registered")

        self._adapters[adapter_id].subscribers.append(handler)
        logger.info(f"Added subscriber to {adapter_id}")

    async def start_all(self) -> None:
        """Start all registered adapters."""
        async with self._lock:
            if self._running:
                logger.warning("DataBridge already running")
                return

            self._running = True
            logger.info("Starting all adapters...")

            for adapter_id, registration in self._adapters.items():
                await self._start_adapter(registration)

    async def _start_adapter(self, registration: AdapterRegistration) -> None:
        """Start a single adapter."""
        if registration.state == AdapterState.RUNNING:
            logger.warning(f"Adapter {registration.adapter_id} already running")
            return

        registration.state = AdapterState.STARTING
        registration.task = asyncio.create_task(
            self._adapter_loop(registration)
        )
        logger.info(f"Started adapter: {registration.adapter_id}")

    async def _adapter_loop(self, registration: AdapterRegistration) -> None:
        """Main loop for an adapter - fetch and distribute data."""
        registration.state = AdapterState.RUNNING

        while self._running:
            try:
                # Fetch data from adapter
                data = await registration.adapter_instance.fetch()

                # Distribute to all subscribers
                for subscriber in registration.subscribers:
                    try:
                        if asyncio.iscoroutinefunction(subscriber):
                            await subscriber(data)
                        else:
                            subscriber(data)
                    except Exception as e:
                        logger.error(
                            f"Subscriber error for {registration.adapter_id}: {e}"
                        )

                # Reset error count on success
                registration.error_count = 0

            except Exception as e:
                registration.error_count += 1
                registration.last_error = str(e)
                logger.error(
                    f"Adapter {registration.adapter_id} error "
                    f"(count: {registration.error_count}): {e}"
                )

                # If too many errors, mark as error state
                if registration.error_count >= 5:
                    registration.state = AdapterState.ERROR
                    logger.error(
                        f"Adapter {registration.adapter_id} entered error state"
                    )
                    break

            # Wait before next poll
            await asyncio.sleep(registration.poll_interval)

        registration.state = AdapterState.STOPPED

    async def stop_all(self) -> None:
        """Stop all running adapters."""
        async with self._lock:
            if not self._running:
                return

            self._running = False
            logger.info("Stopping all adapters...")

            # Cancel all adapter tasks
            tasks = []
            for registration in self._adapters.values():
                if registration.task and not registration.task.done():
                    registration.state = AdapterState.STOPPING
                    registration.task.cancel()
                    tasks.append(registration.task)

            # Wait for all to complete
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

            logger.info("All adapters stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get status of all adapters."""
        return {
            "running": self._running,
            "adapters": {
                adapter_id: {
                    "state": reg.state.value,
                    "subscribers": len(reg.subscribers),
                    "error_count": reg.error_count,
                    "last_error": reg.last_error
                }
                for adapter_id, reg in self._adapters.items()
            }
        }


# Global registry instance
_registry: Optional[DataBridgeRegistry] = None


def get_registry() -> DataBridgeRegistry:
    """Get the global DataBridge registry instance."""
    global _registry
    if _registry is None:
        _registry = DataBridgeRegistry()
    return _registry
