"""
Hooks Registry - Registry for agent lifecycle hooks.

Allows custom logic to be executed at lifecycle events.
"""
import logging
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class HookEvent(Enum):
    """Lifecycle hook events."""
    PRE_START = "pre_start"
    POST_START = "post_start"
    PRE_STOP = "pre_stop"
    POST_STOP = "post_stop"
    PRE_PAUSE = "pre_pause"
    POST_PAUSE = "post_pause"
    PRE_RESUME = "pre_resume"
    POST_RESUME = "post_resume"
    ON_ERROR = "on_error"
    ON_RESTART = "on_restart"


@dataclass
class Hook:
    """Represents a lifecycle hook."""
    event: HookEvent
    callback: Callable
    priority: int = 0
    name: Optional[str] = None


class HooksRegistry:
    """
    Registry for agent lifecycle hooks.

    Responsibilities:
    - Register hooks for lifecycle events
    - Execute hooks in priority order
    - Handle hook errors gracefully
    - Track hook execution
    """

    def __init__(self):
        self._hooks: Dict[HookEvent, List[Hook]] = {
            event: [] for event in HookEvent
        }
        self._execution_count: Dict[str, int] = {}

    def register_hook(
        self,
        event: HookEvent,
        callback: Callable,
        priority: int = 0,
        name: Optional[str] = None
    ) -> None:
        """
        Register a lifecycle hook.

        Args:
            event: Lifecycle event
            callback: Function to call (signature: callback(agent_id, **kwargs))
            priority: Execution priority (higher = earlier)
            name: Optional hook name for identification
        """
        hook = Hook(
            event=event,
            callback=callback,
            priority=priority,
            name=name or f"hook_{len(self._hooks[event])}"
        )

        self._hooks[event].append(hook)

        # Sort by priority (descending)
        self._hooks[event].sort(key=lambda h: h.priority, reverse=True)

        logger.info(f"Registered hook: {hook.name} for {event.value} (priority={priority})")

    def execute_hooks(
        self,
        event: str,
        agent_id: str,
        **kwargs
    ) -> None:
        """
        Execute all hooks for an event.

        Args:
            event: Event name (string)
            agent_id: Agent identifier
            **kwargs: Additional arguments to pass to hooks
        """
        # Convert string to enum
        try:
            hook_event = HookEvent(event)
        except ValueError:
            logger.warning(f"Unknown hook event: {event}")
            return

        hooks = self._hooks.get(hook_event, [])

        if not hooks:
            logger.debug(f"No hooks registered for {event}")
            return

        logger.debug(f"Executing {len(hooks)} hooks for {event} on agent {agent_id}")

        for hook in hooks:
            try:
                hook.callback(agent_id, **kwargs)

                # Track execution
                hook_key = f"{hook_event.value}:{hook.name}"
                self._execution_count[hook_key] =                     self._execution_count.get(hook_key, 0) + 1

                logger.debug(f"Executed hook: {hook.name}")

            except Exception as e:
                logger.error(
                    f"Hook {hook.name} failed for {event} on {agent_id}: {e}",
                    exc_info=True
                )
                # Continue executing other hooks

    def unregister_hook(self, event: HookEvent, name: str) -> bool:
        """
        Unregister a hook by name.

        Args:
            event: Lifecycle event
            name: Hook name

        Returns:
            True if hook was found and removed
        """
        hooks = self._hooks.get(event, [])

        for i, hook in enumerate(hooks):
            if hook.name == name:
                del hooks[i]
                logger.info(f"Unregistered hook: {name} from {event.value}")
                return True

        logger.warning(f"Hook {name} not found for {event.value}")
        return False

    def list_hooks(self, event: Optional[HookEvent] = None) -> Dict[str, List[str]]:
        """
        List registered hooks.

        Args:
            event: Specific event (None = all)

        Returns:
            Dictionary of event -> list of hook names
        """
        if event:
            return {
                event.value: [h.name for h in self._hooks[event]]
            }

        return {
            event.value: [h.name for h in hooks]
            for event, hooks in self._hooks.items()
            if hooks
        }

    def get_execution_stats(self) -> Dict[str, int]:
        """Get hook execution statistics."""
        return self._execution_count.copy()

    def get_status(self) -> Dict[str, Any]:
        """Get registry status."""
        total_hooks = sum(len(hooks) for hooks in self._hooks.values())

        hooks_by_event = {
            event.value: len(self._hooks[event])
            for event in HookEvent
            if self._hooks[event]
        }

        return {
            "total_hooks": total_hooks,
            "hooks_by_event": hooks_by_event,
            "total_executions": sum(self._execution_count.values())
        }


# Global hooks registry instance
_hooks_registry: Optional[HooksRegistry] = None


def get_hooks_registry() -> HooksRegistry:
    """Get the global hooks registry instance."""
    global _hooks_registry
    if _hooks_registry is None:
        _hooks_registry = HooksRegistry()
    return _hooks_registry
