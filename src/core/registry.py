
from typing import Dict, Any, Type, Optional, List
from pydantic import BaseModel

class ComponentManifest(BaseModel):
    id: str
    version: str
    capabilities: List[str]
    priority: int = 0

class CoreRegistry:
    _instance = None
    _components: Dict[str, Any] = {}
    _capabilities: Dict[str, List[str]] = {} # capability -> [component_ids]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CoreRegistry, cls).__new__(cls)
        return cls._instance

    def register(self, component_id: str, instance: Any, manifest: ComponentManifest):
        """
        Registers a component into the native lattice.
        """
        print(f"Registering component: {component_id} with capabilities: {manifest.capabilities}")
        self._components[component_id] = instance

        for cap in manifest.capabilities:
            if cap not in self._capabilities:
                self._capabilities[cap] = []
            self._capabilities[cap].append(component_id)
            # Sort by priority (descending) - simplified logic here
            self._capabilities[cap].sort(key=lambda x: -1) 

    def get_provider(self, capability: str) -> Optional[Any]:
        """
        Returns the best provider for a capability.
        """
        providers = self._capabilities.get(capability, [])
        if not providers:
            return None
        return self._components[providers[0]]

    def introspect(self) -> Dict[str, Any]:
        """
        Returns a full graph of the system for Agent consumption.
        """
        return {
            "components": list(self._components.keys()),
            "capabilities": self._capabilities
        }

# Global Instance
registry = CoreRegistry()
