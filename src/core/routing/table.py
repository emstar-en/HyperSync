
from typing import List, Dict, Any, Callable
from pydantic import BaseModel

class RoutingRule(BaseModel):
    target_processor: str
    predicates: Dict[str, Any] # e.g., {"extension": ".csv", "mime": "text/csv"}
    priority: int

class RoutingTable:
    def __init__(self):
        self.rules: List[RoutingRule] = []

    def add_rule(self, rule: RoutingRule):
        self.rules.append(rule)
        self.rules.sort(key=lambda x: x.priority, reverse=True)

    def match(self, metadata: Dict[str, Any]) -> str:
        """
        Finds the best processor for the given metadata.
        """
        for rule in self.rules:
            if self._check_predicates(rule.predicates, metadata):
                return rule.target_processor
        return "fallback_processor"

    def _check_predicates(self, predicates: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        for key, value in predicates.items():
            if metadata.get(key) != value:
                return False
        return True
