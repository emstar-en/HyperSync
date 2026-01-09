"""
Node Assembly Usage Examples
"""

from hypersync.assembly import AssemblyManager


def example_1_simple_stack():
    """Example 1: Create a simple single-model stack"""
    print("=== Example 1: Simple Stack ===\n")

    manager = AssemblyManager()

    stack = manager.create_stack(
        name="simple-gpt4",
        models=[
            {"role": "main", "model_id": "gpt-4"}
        ]
    )

    print(f"Created stack: {stack.stack_id}")
    print(f"Models: {len(stack.models)}")


def example_2_multi_modal():
    """Example 2: Multi-modal stack"""
    print("\n=== Example 2: Multi-Modal Stack ===\n")

    manager = AssemblyManager()

    stack = manager.create_stack(
        name="multi-modal-assistant",
        models=[
            {"role": "reasoning", "model_id": "gpt-4", "priority": 1},
            {"role": "vision", "model_id": "clip-vit-large", "priority": 2},
            {"role": "audio", "model_id": "whisper-large-v3", "priority": 3}
        ],
        orchestration={"mode": "pipeline"},
        resource_requirements={
            "cpu_cores": 16,
            "memory_gb": 64,
            "gpu_count": 2,
            "gpu_memory_gb": 48
        },
        capabilities=["text", "vision", "audio"],
        tags=["multi-modal", "production"]
    )

    print(f"Created multi-modal stack: {stack.stack_id}")
    print(f"Models: {len(stack.models)}")
    print(f"Capabilities: {stack.capabilities}")


def example_3_router():
    """Example 3: Router stack"""
    print("\n=== Example 3: Router Stack ===\n")

    manager = AssemblyManager()

    stack = manager.create_stack(
        name="smart-router",
        models=[
            {"role": "text", "model_id": "gpt-4"},
            {"role": "code", "model_id": "codex"},
            {"role": "math", "model_id": "minerva"}
        ],
        orchestration={
            "mode": "router",
            "routing_strategy": "capability_based"
        }
    )

    print(f"Created router stack: {stack.stack_id}")
    print(f"Routing strategy: {stack.orchestration['routing_strategy']}")


def example_4_ensemble():
    """Example 4: Ensemble stack"""
    print("\n=== Example 4: Ensemble Stack ===\n")

    manager = AssemblyManager()

    stack = manager.create_stack(
        name="ensemble-qa",
        models=[
            {"role": "qa-1", "model_id": "model-a"},
            {"role": "qa-2", "model_id": "model-b"},
            {"role": "qa-3", "model_id": "model-c"}
        ],
        orchestration={
            "mode": "ensemble",
            "aggregation": "voting"
        }
    )

    print(f"Created ensemble stack: {stack.stack_id}")
    print(f"Aggregation: {stack.orchestration['aggregation']}")


def example_5_assembly_and_deploy():
    """Example 5: Create assembly and deploy"""
    print("\n=== Example 5: Assembly and Deployment ===\n")

    manager = AssemblyManager()

    # Create stack
    stack = manager.create_stack(
        name="production-assistant",
        models=[
            {"role": "main", "model_id": "gpt-4"}
        ]
    )

    print(f"Created stack: {stack.stack_id}")

    # Create assembly
    assembly = manager.create_assembly(
        name="prod-assistant-node",
        stack_id=stack.stack_id,
        target_ld="ld-secure-prod-001",
        security_level="secure",
        tags=["production", "assistant"]
    )

    print(f"Created assembly: {assembly.assembly_id}")
    print(f"Status: {assembly.status}")

    # Validate
    validation = manager.validate_assembly(assembly.assembly_id)
    print(f"\nValidation passed: {validation['passed']}")
    print(f"Checks: {len(validation['checks'])}")

    if validation['passed']:
        # Deploy
        deployment = manager.deploy_assembly(assembly.assembly_id)
        print(f"\nDeployed!")
        print(f"Deployment ID: {deployment.deployment_id}")
        print(f"Node ID: {deployment.node_id}")
        print(f"LD Address: {deployment.ld_address}")
        print(f"Status: {deployment.status}")


def example_6_list_and_query():
    """Example 6: List and query"""
    print("\n=== Example 6: List and Query ===\n")

    manager = AssemblyManager()

    # List stacks
    stacks = manager.list_stacks(limit=10)
    print(f"Total stacks: {len(stacks)}")

    # List by tags
    prod_stacks = manager.list_stacks(tags=["production"])
    print(f"Production stacks: {len(prod_stacks)}")

    # List assemblies
    assemblies = manager.list_assemblies(limit=10)
    print(f"Total assemblies: {len(assemblies)}")

    # List deployed assemblies
    deployed = manager.list_assemblies(status="deployed")
    print(f"Deployed assemblies: {len(deployed)}")

    # List deployments
    deployments = manager.list_deployments(status="running")
    print(f"Running deployments: {len(deployments)}")


if __name__ == "__main__":
    example_1_simple_stack()
    example_2_multi_modal()
    example_3_router()
    example_4_ensemble()
    example_5_assembly_and_deploy()
    example_6_list_and_query()

    print("\n=== All Examples Complete ===")
