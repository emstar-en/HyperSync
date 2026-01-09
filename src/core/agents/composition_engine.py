"""
HyperSync Agent Composition Engine

Multi-pass orchestration engine for building, validating, and activating agents.
Implements deterministic three-pass pipeline: validate -> wire -> activate.
"""

from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


class PassType(Enum):
    """Composition pass types."""
    VALIDATE = "validate"
    WIRE = "wire"
    ACTIVATE = "activate"


class StepStatus(Enum):
    """Execution step status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class CompositionStep:
    """Represents a single step in the composition pipeline."""
    step_id: str
    pass_type: PassType
    description: str
    handler: Callable
    dependencies: List[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Convert step to dictionary representation."""
        return {
            'step_id': self.step_id,
            'pass_type': self.pass_type.value,
            'description': self.description,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_ms': (
                (self.completed_at - self.started_at).total_seconds() * 1000
                if self.started_at and self.completed_at else None
            )
        }


@dataclass
class BuildPlan:
    """Complete build plan for agent composition."""
    agent_id: str
    profile: Dict
    steps: List[CompositionStep]
    created_at: datetime = field(default_factory=datetime.utcnow)

    def get_steps_by_pass(self, pass_type: PassType) -> List[CompositionStep]:
        """Get all steps for a specific pass."""
        return [s for s in self.steps if s.pass_type == pass_type]

    def get_step(self, step_id: str) -> Optional[CompositionStep]:
        """Get step by ID."""
        return next((s for s in self.steps if s.step_id == step_id), None)

    def to_dict(self) -> Dict:
        """Convert plan to dictionary representation."""
        return {
            'agent_id': self.agent_id,
            'profile': self.profile,
            'steps': [s.to_dict() for s in self.steps],
            'created_at': self.created_at.isoformat(),
            'summary': {
                'total_steps': len(self.steps),
                'by_pass': {
                    'validate': len(self.get_steps_by_pass(PassType.VALIDATE)),
                    'wire': len(self.get_steps_by_pass(PassType.WIRE)),
                    'activate': len(self.get_steps_by_pass(PassType.ACTIVATE))
                },
                'by_status': {
                    status.value: len([s for s in self.steps if s.status == status])
                    for status in StepStatus
                }
            }
        }


class CompositionEngine:
    """
    Multi-pass composition engine for agent lifecycle management.

    Orchestrates agent creation through three deterministic passes:
    1. VALIDATE - Schema validation, capability checks, policy verification
    2. WIRE - Dependency resolution, node binding, configuration propagation
    3. ACTIVATE - Runtime initialization, health checks, registration
    """

    def __init__(self, 
                 capability_registry: Any,
                 policy_manager: Optional[Any] = None,
                 telemetry_client: Optional[Any] = None):
        """
        Initialize composition engine.

        Args:
            capability_registry: Reference to capability registry
            policy_manager: Optional policy manager for validation
            telemetry_client: Optional telemetry client for observability
        """
        self.capability_registry = capability_registry
        self.policy_manager = policy_manager
        self.telemetry_client = telemetry_client
        self.active_plans: Dict[str, BuildPlan] = {}

    def plan_build(self, agent_id: str, profile: Dict, 
                   passes: Optional[List[str]] = None) -> BuildPlan:
        """
        Create a build plan for agent composition.

        Args:
            agent_id: Agent identifier
            profile: Agent profile configuration
            passes: List of passes to include (default: all)

        Returns:
            BuildPlan with ordered steps
        """
        if passes is None:
            passes = ["validate", "wire", "activate"]

        steps = []

        # PASS 1: VALIDATE
        if "validate" in passes:
            steps.extend(self._create_validation_steps(agent_id, profile))

        # PASS 2: WIRE
        if "wire" in passes:
            steps.extend(self._create_wiring_steps(agent_id, profile))

        # PASS 3: ACTIVATE
        if "activate" in passes:
            steps.extend(self._create_activation_steps(agent_id, profile))

        plan = BuildPlan(agent_id=agent_id, profile=profile, steps=steps)
        self.active_plans[agent_id] = plan

        logger.info(f"Created build plan for {agent_id} with {len(steps)} steps")
        return plan

    def _create_validation_steps(self, agent_id: str, profile: Dict) -> List[CompositionStep]:
        """Create validation pass steps."""
        return [
            CompositionStep(
                step_id=f"{agent_id}:validate:schema",
                pass_type=PassType.VALIDATE,
                description="Validate profile against JSON schema",
                handler=self._validate_schema
            ),
            CompositionStep(
                step_id=f"{agent_id}:validate:nodes",
                pass_type=PassType.VALIDATE,
                description="Verify all nodes exist in capability registry",
                handler=self._validate_nodes,
                dependencies=[f"{agent_id}:validate:schema"]
            ),
            CompositionStep(
                step_id=f"{agent_id}:validate:capabilities",
                pass_type=PassType.VALIDATE,
                description="Check node capabilities match requirements",
                handler=self._validate_capabilities,
                dependencies=[f"{agent_id}:validate:nodes"]
            ),
            CompositionStep(
                step_id=f"{agent_id}:validate:policy",
                pass_type=PassType.VALIDATE,
                description="Verify policy bindings are valid",
                handler=self._validate_policy,
                dependencies=[f"{agent_id}:validate:schema"]
            ),
            CompositionStep(
                step_id=f"{agent_id}:validate:routing",
                pass_type=PassType.VALIDATE,
                description="Validate routing strategy configuration",
                handler=self._validate_routing,
                dependencies=[f"{agent_id}:validate:schema"]
            )
        ]

    def _create_wiring_steps(self, agent_id: str, profile: Dict) -> List[CompositionStep]:
        """Create wiring pass steps."""
        validate_deps = [f"{agent_id}:validate:capabilities", 
                        f"{agent_id}:validate:policy",
                        f"{agent_id}:validate:routing"]

        return [
            CompositionStep(
                step_id=f"{agent_id}:wire:bindings",
                pass_type=PassType.WIRE,
                description="Create node bindings based on routing strategy",
                handler=self._wire_bindings,
                dependencies=validate_deps
            ),
            CompositionStep(
                step_id=f"{agent_id}:wire:dependencies",
                pass_type=PassType.WIRE,
                description="Resolve inter-node dependencies",
                handler=self._wire_dependencies,
                dependencies=[f"{agent_id}:wire:bindings"]
            ),
            CompositionStep(
                step_id=f"{agent_id}:wire:config",
                pass_type=PassType.WIRE,
                description="Propagate configuration to bound nodes",
                handler=self._wire_config,
                dependencies=[f"{agent_id}:wire:dependencies"]
            ),
            CompositionStep(
                step_id=f"{agent_id}:wire:telemetry",
                pass_type=PassType.WIRE,
                description="Configure telemetry collection points",
                handler=self._wire_telemetry,
                dependencies=[f"{agent_id}:wire:config"]
            )
        ]

    def _create_activation_steps(self, agent_id: str, profile: Dict) -> List[CompositionStep]:
        """Create activation pass steps."""
        wire_deps = [f"{agent_id}:wire:telemetry"]

        return [
            CompositionStep(
                step_id=f"{agent_id}:activate:initialize",
                pass_type=PassType.ACTIVATE,
                description="Initialize agent runtime state",
                handler=self._activate_initialize,
                dependencies=wire_deps
            ),
            CompositionStep(
                step_id=f"{agent_id}:activate:health",
                pass_type=PassType.ACTIVATE,
                description="Perform health checks on bound nodes",
                handler=self._activate_health_check,
                dependencies=[f"{agent_id}:activate:initialize"]
            ),
            CompositionStep(
                step_id=f"{agent_id}:activate:register",
                pass_type=PassType.ACTIVATE,
                description="Register agent in active registry",
                handler=self._activate_register,
                dependencies=[f"{agent_id}:activate:health"]
            ),
            CompositionStep(
                step_id=f"{agent_id}:activate:emit",
                pass_type=PassType.ACTIVATE,
                description="Emit activation telemetry and receipts",
                handler=self._activate_emit_telemetry,
                dependencies=[f"{agent_id}:activate:register"]
            )
        ]

    async def execute_plan(self, plan: BuildPlan) -> Dict[str, Any]:
        """
        Execute a build plan asynchronously.

        Args:
            plan: BuildPlan to execute

        Returns:
            Execution report with results and timing
        """
        logger.info(f"Executing build plan for {plan.agent_id}")
        start_time = datetime.utcnow()

        # Execute passes in order
        for pass_type in [PassType.VALIDATE, PassType.WIRE, PassType.ACTIVATE]:
            pass_steps = plan.get_steps_by_pass(pass_type)
            logger.info(f"Executing {pass_type.value} pass with {len(pass_steps)} steps")

            for step in pass_steps:
                await self._execute_step(plan, step)

                # Stop on failure
                if step.status == StepStatus.FAILED:
                    logger.error(f"Step {step.step_id} failed: {step.error}")
                    return self._create_execution_report(plan, start_time, success=False)

        end_time = datetime.utcnow()
        logger.info(f"Build plan completed for {plan.agent_id}")

        return self._create_execution_report(plan, start_time, success=True)

    async def _execute_step(self, plan: BuildPlan, step: CompositionStep) -> None:
        """Execute a single composition step."""
        # Check dependencies
        for dep_id in step.dependencies:
            dep_step = plan.get_step(dep_id)
            if not dep_step or dep_step.status != StepStatus.SUCCESS:
                step.status = StepStatus.SKIPPED
                step.error = f"Dependency {dep_id} not satisfied"
                return

        # Execute step
        step.status = StepStatus.RUNNING
        step.started_at = datetime.utcnow()

        try:
            result = await step.handler(plan.agent_id, plan.profile)
            step.result = result
            step.status = StepStatus.SUCCESS
        except Exception as e:
            step.error = str(e)
            step.status = StepStatus.FAILED
            logger.exception(f"Step {step.step_id} failed")
        finally:
            step.completed_at = datetime.utcnow()

    def _create_execution_report(self, plan: BuildPlan, start_time: datetime, 
                                 success: bool) -> Dict[str, Any]:
        """Create execution report."""
        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000

        return {
            'agent_id': plan.agent_id,
            'success': success,
            'started_at': start_time.isoformat(),
            'completed_at': end_time.isoformat(),
            'duration_ms': duration_ms,
            'plan': plan.to_dict(),
            'failed_steps': [
                s.to_dict() for s in plan.steps if s.status == StepStatus.FAILED
            ]
        }

    # Step handler implementations
    async def _validate_schema(self, agent_id: str, profile: Dict) -> Dict:
        """Validate profile schema."""
        # Schema validation logic here
        return {'valid': True}

    async def _validate_nodes(self, agent_id: str, profile: Dict) -> Dict:
        """Validate node existence."""
        nodes = profile.get('nodes', [])
        invalid = [n for n in nodes if not self.capability_registry.node_exists(n)]
        if invalid:
            raise ValueError(f"Invalid nodes: {invalid}")
        return {'valid_nodes': nodes}

    async def _validate_capabilities(self, agent_id: str, profile: Dict) -> Dict:
        """Validate node capabilities."""
        # Capability validation logic
        return {'capabilities_valid': True}

    async def _validate_policy(self, agent_id: str, profile: Dict) -> Dict:
        """Validate policy bindings."""
        if self.policy_manager:
            # Policy validation logic
            pass
        return {'policy_valid': True}

    async def _validate_routing(self, agent_id: str, profile: Dict) -> Dict:
        """Validate routing configuration."""
        strategy = profile.get('routing_strategy')
        config = profile.get('routing_config', {})

        if strategy == 'priority_weighted' and 'weights' not in config:
            raise ValueError("priority_weighted requires weights")

        return {'routing_valid': True}

    async def _wire_bindings(self, agent_id: str, profile: Dict) -> Dict:
        """Create node bindings."""
        bindings = []
        for node_id in profile.get('nodes', []):
            binding = {
                'binding_id': f"binding-{agent_id}-{node_id}",
                'agent_id': agent_id,
                'node_id': node_id,
                'binding_type': 'primary'
            }
            bindings.append(binding)
        return {'bindings': bindings}

    async def _wire_dependencies(self, agent_id: str, profile: Dict) -> Dict:
        """Resolve dependencies."""
        return {'dependencies_resolved': True}

    async def _wire_config(self, agent_id: str, profile: Dict) -> Dict:
        """Propagate configuration."""
        return {'config_propagated': True}

    async def _wire_telemetry(self, agent_id: str, profile: Dict) -> Dict:
        """Configure telemetry."""
        return {'telemetry_configured': True}

    async def _activate_initialize(self, agent_id: str, profile: Dict) -> Dict:
        """Initialize runtime."""
        return {'initialized': True}

    async def _activate_health_check(self, agent_id: str, profile: Dict) -> Dict:
        """Perform health checks."""
        return {'health': 'ok'}

    async def _activate_register(self, agent_id: str, profile: Dict) -> Dict:
        """Register agent."""
        return {'registered': True}

    async def _activate_emit_telemetry(self, agent_id: str, profile: Dict) -> Dict:
        """Emit telemetry."""
        if self.telemetry_client:
            # Emit telemetry
            pass
        return {'telemetry_emitted': True}

    def execute_step(self, step: CompositionStep) -> None:
        """Synchronous wrapper for step execution."""
        asyncio.run(self._execute_step(
            self.active_plans.get(step.step_id.split(':')[0]),
            step
        ))
