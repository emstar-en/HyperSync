"""
Knowledge Graph Engine - Ontology management with reasoning.

Provides ontology management, reasoning hooks, SPARQL endpoint,
and entity linking pipeline.
"""
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum


class RelationType(Enum):
    """Ontology relation types."""
    IS_A = "is_a"
    PART_OF = "part_of"
    RELATED_TO = "related_to"
    INSTANCE_OF = "instance_of"


@dataclass
class Entity:
    """Knowledge graph entity."""
    entity_id: str
    entity_type: str
    properties: Dict[str, Any]
    embeddings: Optional[List[float]] = None


@dataclass
class Relation:
    """Knowledge graph relation."""
    relation_id: str
    relation_type: RelationType
    source: str
    target: str
    properties: Dict[str, Any]


@dataclass
class Ontology:
    """Ontology definition."""
    ontology_id: str
    name: str
    classes: Dict[str, Dict[str, Any]]
    properties: Dict[str, Dict[str, Any]]


class KnowledgeGraphEngine:
    """
    Knowledge graph storage and reasoning engine.

    Manages entities, relations, and ontologies with reasoning
    capabilities and SPARQL query support.
    """

    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relations: Dict[str, Relation] = {}
        self.ontologies: Dict[str, Ontology] = {}
        self.type_hierarchy: Dict[str, Set[str]] = {}  # type -> supertypes

    def add_entity(self, entity_id: str, entity_type: str,
                   properties: Optional[Dict[str, Any]] = None,
                   embeddings: Optional[List[float]] = None) -> Entity:
        """
        Add entity to knowledge graph.

        Args:
            entity_id: Entity identifier
            entity_type: Entity type
            properties: Entity properties
            embeddings: Optional embeddings

        Returns:
            Created Entity
        """
        entity = Entity(
            entity_id=entity_id,
            entity_type=entity_type,
            properties=properties or {},
            embeddings=embeddings
        )

        self.entities[entity_id] = entity
        return entity

    def add_relation(self, source: str, target: str,
                    relation_type: RelationType,
                    properties: Optional[Dict[str, Any]] = None) -> Relation:
        """
        Add relation between entities.

        Args:
            source: Source entity ID
            target: Target entity ID
            relation_type: Type of relation
            properties: Relation properties

        Returns:
            Created Relation
        """
        relation_id = f"{source}_{relation_type.value}_{target}"

        relation = Relation(
            relation_id=relation_id,
            relation_type=relation_type,
            source=source,
            target=target,
            properties=properties or {}
        )

        self.relations[relation_id] = relation

        # Update type hierarchy for IS_A relations
        if relation_type == RelationType.IS_A:
            if source not in self.type_hierarchy:
                self.type_hierarchy[source] = set()
            self.type_hierarchy[source].add(target)

        return relation

    def query_sparql(self, sparql: str) -> List[Dict[str, Any]]:
        """
        Execute SPARQL query (simplified implementation).

        Args:
            sparql: SPARQL query string

        Returns:
            Query results
        """
        # Simplified SPARQL parser - production would use rdflib
        results = []

        if "SELECT" in sparql:
            # Extract pattern matching
            if "?s ?p ?o" in sparql:
                # Return all triples
                for relation in self.relations.values():
                    results.append({
                        "s": relation.source,
                        "p": relation.relation_type.value,
                        "o": relation.target
                    })

        return results

    def infer_relations(self, entity_id: str) -> List[Relation]:
        """
        Infer implicit relations using reasoning.

        Args:
            entity_id: Entity to infer relations for

        Returns:
            List of inferred relations
        """
        inferred = []

        if entity_id not in self.entities:
            return inferred

        entity = self.entities[entity_id]

        # Transitive closure of IS_A relations
        supertypes = self._get_all_supertypes(entity.entity_type)

        for supertype in supertypes:
            # Infer INSTANCE_OF relations
            relation = Relation(
                relation_id=f"{entity_id}_instance_of_{supertype}",
                relation_type=RelationType.INSTANCE_OF,
                source=entity_id,
                target=supertype,
                properties={"inferred": True}
            )
            inferred.append(relation)

        return inferred

    def link_entities(self, text: str, embeddings: Optional[List[float]] = None) -> List[Tuple[str, float]]:
        """
        Link text mentions to entities.

        Args:
            text: Text to link
            embeddings: Optional text embeddings

        Returns:
            List of (entity_id, confidence) tuples
        """
        linked = []
        text_lower = text.lower()

        # Simple string matching (production would use NER + embeddings)
        for entity_id, entity in self.entities.items():
            if entity_id.lower() in text_lower:
                linked.append((entity_id, 0.9))
            elif any(str(v).lower() in text_lower for v in entity.properties.values()):
                linked.append((entity_id, 0.7))

        # If embeddings provided, use semantic similarity
        if embeddings:
            for entity_id, entity in self.entities.items():
                if entity.embeddings:
                    similarity = self._cosine_similarity(embeddings, entity.embeddings)
                    if similarity > 0.8:
                        linked.append((entity_id, similarity))

        # Sort by confidence
        linked.sort(key=lambda x: x[1], reverse=True)
        return linked

    def add_ontology(self, ontology_id: str, name: str,
                    classes: Optional[Dict[str, Dict[str, Any]]] = None,
                    properties: Optional[Dict[str, Dict[str, Any]]] = None) -> Ontology:
        """
        Add ontology definition.

        Args:
            ontology_id: Ontology identifier
            name: Ontology name
            classes: Class definitions
            properties: Property definitions

        Returns:
            Created Ontology
        """
        ontology = Ontology(
            ontology_id=ontology_id,
            name=name,
            classes=classes or {},
            properties=properties or {}
        )

        self.ontologies[ontology_id] = ontology
        return ontology

    def _get_all_supertypes(self, entity_type: str) -> Set[str]:
        """Get all supertypes through transitive closure."""
        supertypes = set()

        if entity_type in self.type_hierarchy:
            for supertype in self.type_hierarchy[entity_type]:
                supertypes.add(supertype)
                supertypes.update(self._get_all_supertypes(supertype))

        return supertypes

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Compute cosine similarity."""
        if len(v1) != len(v2):
            return 0.0

        import math
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(x**2 for x in v1))
        norm2 = math.sqrt(sum(x**2 for x in v2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot / (norm1 * norm2)

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge graph statistics."""
        return {
            "num_entities": len(self.entities),
            "num_relations": len(self.relations),
            "num_ontologies": len(self.ontologies),
            "num_types": len(self.type_hierarchy)
        }
