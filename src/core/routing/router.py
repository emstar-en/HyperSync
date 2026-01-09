
from typing import Any, Dict
from ..registry import registry, ComponentManifest
from .table import RoutingTable, RoutingRule
from .detector import FormatDetector

class FormatRouter:
    def __init__(self):
        self.manifest = ComponentManifest(
            id="core_format_router",
            version="1.2.0",
            capabilities=["data_ingestion", "format_detection", "routing"],
            priority=100
        )
        self.table = RoutingTable()
        self.detector = FormatDetector()
        self._load_defaults()
        self._register()

    def _load_defaults(self):
        self.table.add_rule(RoutingRule(
            target_processor="core_ustab_processor",
            predicates={"mime": "text/csv"},
            priority=10
        ))
        self.table.add_rule(RoutingRule(
            target_processor="core_ustab_processor",
            predicates={"extension": ".csv"},
            priority=9
        ))

    def _register(self):
        registry.register(self.manifest.id, self, self.manifest)

    def route(self, data: Any, filename: str = "") -> Dict[str, Any]:
        """
        Full pipeline: Detect -> Match -> Return Decision
        """
        # 1. Detect
        metadata = self.detector.detect(data, filename)

        # 2. Match
        target = self.table.match(metadata)

        return {
            "decision": "routed",
            "target": target,
            "metadata": metadata
        }

# Auto-initialize
default_router = FormatRouter()
