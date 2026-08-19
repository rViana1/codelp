"""Graph-aware, explainable enrichment of semantic retrieval results."""

from __future__ import annotations

from collections import defaultdict

from core.project import ProjectKnowledgeGraph

from .models import RetrievalCollection, RetrievalResult


class IntelligentRetrievalEngine:
    """Combine semantic ranking with current and historical graph evidence."""

    STRUCTURAL_KINDS = {
        "chunk_duplicates_chunk": 1.0,
        "chunk_similar_to_chunk": 0.8,
        "symbol_has_chunk": 0.45,
        "file_declares_symbol": 0.35,
        "file_depends_on_file": 0.35,
    }

    def __init__(
        self,
        *,
        semantic_weight: float = 0.70,
        structural_weight: float = 0.25,
        historical_weight: float = 0.05,
    ) -> None:
        weights = (semantic_weight, structural_weight, historical_weight)
        if any(weight < 0 or weight > 1 for weight in weights):
            raise ValueError("Retrieval weights must be between 0 and 1")
        if abs(sum(weights) - 1.0) > 1e-9:
            raise ValueError("Retrieval weights must total 1.0")
        self.semantic_weight = semantic_weight
        self.structural_weight = structural_weight
        self.historical_weight = historical_weight

    def enrich(
        self,
        retrieval: RetrievalCollection,
        graph: ProjectKnowledgeGraph,
    ) -> RetrievalCollection:
        entities = {item.entity_id: item for item in graph.entities}
        chunk_entity_by_identity = {
            item.source_identity: item.entity_id
            for item in graph.entities
            if item.kind == "chunk" and item.is_current
        }
        chunk_identity_by_entity = {
            entity_id: identity
            for identity, entity_id in chunk_entity_by_identity.items()
        }
        adjacency = defaultdict(list)
        for relation in graph.relationships:
            adjacency[relation.source_entity_id].append(relation)
            adjacency[relation.target_entity_id].append(relation)
        for relations in adjacency.values():
            relations.sort(key=lambda item: item.relationship_id)

        semantic = {
            item.chunk_id: (
                item.semantic_score
                if item.semantic_score is not None
                else item.score
            )
            for item in retrieval.results
        }
        evidence: dict[str, set[tuple[str, str, str]]] = defaultdict(set)
        structural: dict[str, float] = defaultdict(float)
        historical: dict[str, float] = defaultdict(float)

        for seed_id, seed_score in sorted(semantic.items()):
            start = chunk_entity_by_identity.get(seed_id)
            if start is None:
                continue
            evidence[seed_id].add(("semantic_match", "", start))
            for target_id, weight, path in self._structural_candidates(
                start,
                adjacency,
                chunk_identity_by_entity,
            ):
                structural[target_id] = max(
                    structural[target_id], seed_score * weight
                )
                kinds = " -> ".join(item[0].kind for item in path)
                for relation, reached_entity_id in path:
                    evidence[target_id].add(
                        (
                            f"structural path through {kinds}",
                            relation.relationship_id,
                            reached_entity_id,
                        )
                    )

            self._add_ancestry_evidence(
                start,
                adjacency,
                entities,
                evidence[seed_id],
                historical,
                seed_id,
            )

        candidates = set(semantic) | set(structural) | set(historical)
        results = []
        for chunk_id in candidates:
            semantic_score = semantic.get(chunk_id, 0.0)
            structural_score = min(structural[chunk_id], 1.0)
            historical_score = min(historical[chunk_id], 1.0)
            final_score = (
                semantic_score * self.semantic_weight
                + structural_score * self.structural_weight
                + historical_score * self.historical_weight
            )
            facts = sorted(evidence[chunk_id])
            results.append(
                RetrievalResult(
                    chunk_id=chunk_id,
                    score=final_score,
                    semantic_score=semantic_score,
                    structural_score=structural_score,
                    historical_score=historical_score,
                    reasons=tuple(sorted({fact[0] for fact in facts})),
                    relationship_ids=tuple(
                        sorted({fact[1] for fact in facts if fact[1]})
                    ),
                    provenance_entity_ids=tuple(
                        sorted({fact[2] for fact in facts if fact[2]})
                    ),
                )
            )
        results.sort(key=lambda item: (-item.score, item.chunk_id))
        return RetrievalCollection(
            query=retrieval.query,
            results=results[: retrieval.query.limit],
        )

    def _structural_candidates(
        self,
        start,
        adjacency,
        chunk_identity_by_entity,
    ):
        candidates = {}
        frontier = [(start, 1.0, ())]
        best_weight = {start: 1.0}
        for _ in range(5):
            following = []
            for entity_id, path_weight, path in sorted(
                frontier,
                key=lambda item: (
                    item[0],
                    -item[1],
                    tuple(step[0].relationship_id for step in item[2]),
                ),
            ):
                for relation in adjacency[entity_id]:
                    if not relation.is_current:
                        continue
                    edge_weight = self.STRUCTURAL_KINDS.get(relation.kind)
                    if edge_weight is None:
                        continue
                    other = self._other(relation, entity_id)
                    relation_score = float(
                        relation.properties.get("score", "1")
                    )
                    weight = path_weight * edge_weight * relation_score
                    if weight <= best_weight.get(other, 0.0):
                        continue
                    best_weight[other] = weight
                    next_path = path + ((relation, other),)
                    following.append((other, weight, next_path))
                    target_id = chunk_identity_by_entity.get(other)
                    if target_id is not None and other != start:
                        current = candidates.get(target_id)
                        if current is None or weight > current[0]:
                            candidates[target_id] = (weight, next_path)
            frontier = following
        return tuple(
            (target_id, value[0], value[1])
            for target_id, value in sorted(candidates.items())
        )

    def _add_ancestry_evidence(
        self,
        start,
        adjacency,
        entities,
        facts,
        historical,
        chunk_id,
    ):
        frontier = [start]
        visited = {start}
        for _ in range(3):
            following = []
            for entity_id in sorted(frontier):
                for relation in adjacency[entity_id]:
                    other = self._other(relation, entity_id)
                    if other not in entities:
                        continue
                    if not relation.is_current:
                        historical[chunk_id] = max(historical[chunk_id], 0.2)
                        facts.add(
                            (
                                f"historical evidence from {relation.kind}",
                                relation.relationship_id,
                                other,
                            )
                        )
                    if other not in visited:
                        visited.add(other)
                        following.append(other)
            frontier = following

    @staticmethod
    def _other(relation, entity_id):
        if relation.source_entity_id == entity_id:
            return relation.target_entity_id
        return relation.source_entity_id
