"""
HyperSync Agent Lifecycle Tasks

Async task implementations for agent lifecycle operations:
create, update, delete, suspend, resume.
"""

import asyncio
import logging
from typing import Dict, Optional, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class LifecycleOperation(Enum):
    """Agent lifecycle operations."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SUSPEND = "suspend"
    RESUME = "resume"
    RESTART = "restart"


class LifecycleTaskManager:
    """
    Manages async lifecycle tasks for agents.
    Coordinates between profile registry, composition engine, and runtime.
    """

    def __init__(self, 
                 profile_registry: Any,
                 composition_engine: Any,
                 runtime_manager: Optional[Any] = None):
        """
        Initialize lifecycle task manager.

        Args:
            profile_registry: Agent profile registry
            composition_engine: Composition engine for building agents
            runtime_manager: Optional runtime manager for active agents
        """
        self.profile_registry = profile_registry
        self.composition_engine = composition_engine
        self.runtime_manager = runtime_manager
        self.active_tasks: Dict[str, asyncio.Task] = {}

    async def create_agent(self, profile_data: Dict, 
                          auto_activate: bool = True) -> Dict[str, Any]:
        """
        Create a new agent from profile data.

        Args:
            profile_data: Agent profile configuration
            auto_activate: Whether to automatically activate after creation

        Returns:
            Creation result with agent_id and status
        """
        logger.info(f"Creating agent: {profile_data.get('name')}")
        start_time = datetime.utcnow()

        try:
            # Step 1: Create profile in registry
            agent_id = self.profile_registry.create_profile(profile_data)
            logger.info(f"Profile created: {agent_id}")

            # Step 2: Build composition plan
            profile = self.profile_registry.get_profile(agent_id)
            plan = self.composition_engine.plan_build(agent_id, profile)
            logger.info(f"Build plan created with {len(plan.steps)} steps")

            # Step 3: Execute composition
            execution_report = await self.composition_engine.execute_plan(plan)

            if not execution_report['success']:
                logger.error(f"Composition failed for {agent_id}")
                # Rollback profile creation
                self.profile_registry.delete_profile(agent_id)
                raise RuntimeError(f"Agent composition failed: {execution_report['failed_steps']}")

            # Step 4: Auto-activate if requested
            if auto_activate:
                self.profile_registry.activate_profile(agent_id)
                logger.info(f"Agent {agent_id} activated")

            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            return {
                'operation': LifecycleOperation.CREATE.value,
                'agent_id': agent_id,
                'success': True,
                'duration_ms': duration_ms,
                'execution_report': execution_report,
                'activated': auto_activate
            }

        except Exception as e:
            logger.exception(f"Failed to create agent: {e}")
            return {
                'operation': LifecycleOperation.CREATE.value,
                'success': False,
                'error': str(e)
            }

    async def update_agent(self, agent_id: str, updates: Dict,
                          rebuild: bool = True) -> Dict[str, Any]:
        """
        Update an existing agent.

        Args:
            agent_id: Agent identifier
            updates: Profile updates to apply
            rebuild: Whether to rebuild composition after update

        Returns:
            Update result with status
        """
        logger.info(f"Updating agent: {agent_id}")
        start_time = datetime.utcnow()

        try:
            # Step 1: Validate agent exists
            profile = self.profile_registry.get_profile(agent_id)
            if not profile:
                raise ValueError(f"Agent {agent_id} not found")

            # Step 2: Check if agent is active
            was_active = profile.get('lifecycle', {}).get('state') == 'active'

            # Step 3: Suspend if active and rebuild requested
            if was_active and rebuild:
                await self.suspend_agent(agent_id)

            # Step 4: Apply updates
            self.profile_registry.update_profile(agent_id, updates)
            logger.info(f"Profile updated: {agent_id}")

            # Step 5: Rebuild if requested
            execution_report = None
            if rebuild:
                updated_profile = self.profile_registry.get_profile(agent_id)
                plan = self.composition_engine.plan_build(agent_id, updated_profile)
                execution_report = await self.composition_engine.execute_plan(plan)

                if not execution_report['success']:
                    logger.error(f"Rebuild failed for {agent_id}")
                    raise RuntimeError(f"Agent rebuild failed: {execution_report['failed_steps']}")

            # Step 6: Reactivate if was active
            if was_active and rebuild:
                await self.resume_agent(agent_id)

            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            return {
                'operation': LifecycleOperation.UPDATE.value,
                'agent_id': agent_id,
                'success': True,
                'duration_ms': duration_ms,
                'rebuilt': rebuild,
                'execution_report': execution_report
            }

        except Exception as e:
            logger.exception(f"Failed to update agent {agent_id}: {e}")
            return {
                'operation': LifecycleOperation.UPDATE.value,
                'agent_id': agent_id,
                'success': False,
                'error': str(e)
            }

    async def delete_agent(self, agent_id: str, 
                          force: bool = False) -> Dict[str, Any]:
        """
        Delete an agent.

        Args:
            agent_id: Agent identifier
            force: Force deletion even if active

        Returns:
            Deletion result with status
        """
        logger.info(f"Deleting agent: {agent_id}")
        start_time = datetime.utcnow()

        try:
            # Step 1: Validate agent exists
            profile = self.profile_registry.get_profile(agent_id)
            if not profile:
                raise ValueError(f"Agent {agent_id} not found")

            # Step 2: Check if active
            is_active = profile.get('lifecycle', {}).get('state') == 'active'

            if is_active and not force:
                raise ValueError(f"Agent {agent_id} is active. Use force=True to delete.")

            # Step 3: Suspend if active
            if is_active:
                await self.suspend_agent(agent_id)

            # Step 4: Cleanup runtime resources
            if self.runtime_manager:
                await self.runtime_manager.cleanup_agent(agent_id)

            # Step 5: Delete profile
            self.profile_registry.delete_profile(agent_id)
            logger.info(f"Agent deleted: {agent_id}")

            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            return {
                'operation': LifecycleOperation.DELETE.value,
                'agent_id': agent_id,
                'success': True,
                'duration_ms': duration_ms,
                'forced': force
            }

        except Exception as e:
            logger.exception(f"Failed to delete agent {agent_id}: {e}")
            return {
                'operation': LifecycleOperation.DELETE.value,
                'agent_id': agent_id,
                'success': False,
                'error': str(e)
            }

    async def suspend_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Suspend an active agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Suspension result with status
        """
        logger.info(f"Suspending agent: {agent_id}")

        try:
            # Step 1: Validate agent exists and is active
            profile = self.profile_registry.get_profile(agent_id)
            if not profile:
                raise ValueError(f"Agent {agent_id} not found")

            state = profile.get('lifecycle', {}).get('state')
            if state != 'active':
                raise ValueError(f"Agent {agent_id} is not active (state: {state})")

            # Step 2: Suspend runtime
            if self.runtime_manager:
                await self.runtime_manager.suspend_agent(agent_id)

            # Step 3: Update profile state
            self.profile_registry.update_profile(agent_id, {
                'lifecycle': {'state': 'suspended'}
            })

            logger.info(f"Agent suspended: {agent_id}")

            return {
                'operation': LifecycleOperation.SUSPEND.value,
                'agent_id': agent_id,
                'success': True
            }

        except Exception as e:
            logger.exception(f"Failed to suspend agent {agent_id}: {e}")
            return {
                'operation': LifecycleOperation.SUSPEND.value,
                'agent_id': agent_id,
                'success': False,
                'error': str(e)
            }

    async def resume_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Resume a suspended agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Resume result with status
        """
        logger.info(f"Resuming agent: {agent_id}")

        try:
            # Step 1: Validate agent exists and is suspended
            profile = self.profile_registry.get_profile(agent_id)
            if not profile:
                raise ValueError(f"Agent {agent_id} not found")

            state = profile.get('lifecycle', {}).get('state')
            if state not in ['suspended', 'draft']:
                raise ValueError(f"Agent {agent_id} cannot be resumed (state: {state})")

            # Step 2: Resume runtime
            if self.runtime_manager:
                await self.runtime_manager.resume_agent(agent_id)

            # Step 3: Update profile state
            self.profile_registry.activate_profile(agent_id)

            logger.info(f"Agent resumed: {agent_id}")

            return {
                'operation': LifecycleOperation.RESUME.value,
                'agent_id': agent_id,
                'success': True
            }

        except Exception as e:
            logger.exception(f"Failed to resume agent {agent_id}: {e}")
            return {
                'operation': LifecycleOperation.RESUME.value,
                'agent_id': agent_id,
                'success': False,
                'error': str(e)
            }

    async def restart_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Restart an agent (suspend + resume).

        Args:
            agent_id: Agent identifier

        Returns:
            Restart result with status
        """
        logger.info(f"Restarting agent: {agent_id}")

        try:
            # Suspend
            suspend_result = await self.suspend_agent(agent_id)
            if not suspend_result['success']:
                raise RuntimeError(f"Suspend failed: {suspend_result.get('error')}")

            # Brief pause
            await asyncio.sleep(0.5)

            # Resume
            resume_result = await self.resume_agent(agent_id)
            if not resume_result['success']:
                raise RuntimeError(f"Resume failed: {resume_result.get('error')}")

            return {
                'operation': LifecycleOperation.RESTART.value,
                'agent_id': agent_id,
                'success': True
            }

        except Exception as e:
            logger.exception(f"Failed to restart agent {agent_id}: {e}")
            return {
                'operation': LifecycleOperation.RESTART.value,
                'agent_id': agent_id,
                'success': False,
                'error': str(e)
            }

    def get_active_tasks(self) -> Dict[str, Dict]:
        """Get status of all active lifecycle tasks."""
        return {
            task_id: {
                'done': task.done(),
                'cancelled': task.cancelled()
            }
            for task_id, task in self.active_tasks.items()
        }
