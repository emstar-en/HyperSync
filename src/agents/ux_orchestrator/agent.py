
from typing import Optional
from ...core.registry import registry, ComponentManifest
from .intent_parser import IntentParser
from .sub_agents import UXDesigner, IntegrationCoordinator, DocumentationManager

class UXOrchestrator:
    def __init__(self, playbooks_dir: str):
        self.manifest = ComponentManifest(
            id="ux_orchestrator",
            version="1.0.0",
            capabilities=["intent_propagation", "system_guidance"],
            priority=100
        )
        self.parser = IntentParser(playbooks_dir)

        # Initialize Sub-Agents
        self.designer = UXDesigner()
        self.coordinator = IntegrationCoordinator()
        self.doc_manager = DocumentationManager()

        self._register()

    def _register(self):
        registry.register(self.manifest.id, self, self.manifest)

    def process_request(self, user_input: str) -> str:
        """
        Main entry point for user interaction.
        """
        # 1. Parse Intent
        playbook = self.parser.parse(user_input)

        if not playbook:
            return "I'm not sure how to help with that yet. Try asking to 'add an extension'."

        # 2. Execute Playbook Logic (Simplified)
        if playbook.name == "create_extension":
            return self._run_create_extension_flow(user_input)

        return f"Found playbook {playbook.name}, but no execution logic defined."

    def _run_create_extension_flow(self, input_text: str) -> str:
        # This mirrors the steps in create_extension.md

        # Step 1: Introspect
        system_state = registry.introspect()

        # Step 2: Guide
        return (
            f"I see you want to extend the system. "
            f"Current capabilities include: {list(system_state['capabilities'].keys())}. "
            f"I have engaged the Integration Coordinator to check for conflicts. "
            f"Please provide the 'id' and 'capabilities' for your new component."
        )

# Factory for main.py
def create_orchestrator():
    # Assuming standard path structure relative to execution
    pb_path = "HyperSync_Spec_Extracted/HyperSync_Spec/04_components/agents/ux_orchestrator/playbooks"
    return UXOrchestrator(pb_path)
