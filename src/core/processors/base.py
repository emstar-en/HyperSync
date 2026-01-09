
from abc import ABC, abstractmethod
from typing import Any, Dict
from ..registry import registry, ComponentManifest
from ..uir.base import BaseUIR

class BaseProcessor(ABC):
    def __init__(self, id: str, input_types: list, output_type: str):
        self.manifest = ComponentManifest(
            id=id,
            version="1.0.0",
            capabilities=[f"process_{output_type.lower()}"],
            priority=10
        )
        self.input_types = input_types
        self.output_type = output_type
        self._register()

    def _register(self):
        registry.register(self.manifest.id, self, self.manifest)

    @abstractmethod
    def process(self, data: Any, metadata: Dict[str, Any]) -> BaseUIR:
        pass
