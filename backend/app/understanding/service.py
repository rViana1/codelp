"""Application service for storage-independent project knowledge exploration."""

from __future__ import annotations

from core.project import Project, ProjectKnowledgeGraph


class ProjectKnowledgeService:
    """Expose graph knowledge without exposing graph or storage internals."""

    RELATED_KINDS = {
        "file_duplicates_file",
        "symbol_duplicates_symbol",
        "chunk_duplicates_chunk",
        "chunk_similar_to_chunk",
    }
    HISTORY_KINDS = {
        "file_has_location",
        "file_has_content_state",
        "location_moved_to",
        "location_renamed_to",
        "location_moved_and_renamed_to",
        "content_state_evolved_to",
    }

    def explore_project(self, project: Project) -> dict[str, object]:
        graph = self._graph(project)
        if graph is None:
            return self._unavailable(project)
        current_entities = [item for item in graph.entities if item.is_current]
        return {
            "project_id": graph.project_id,
            "graph_id": graph.graph_id,
            "entity_counts": self._counts(current_entities),
            "relationship_counts": self._counts(
                item for item in graph.relationships if item.is_current
            ),
            "historical_entities": sum(
                not item.is_current for item in graph.entities
            ),
            "historical_relationships": sum(
                not item.is_current for item in graph.relationships
            ),
        }

    def explore_symbol(
        self, project: Project, symbol_id: str
    ) -> dict[str, object] | None:
        graph = self._graph(project)
        if graph is None:
            return None
        return self._entity_neighbourhood(graph, "symbol", symbol_id)

    def explore_dependencies(
        self, project: Project, file_id: str | None = None
    ) -> list[dict[str, object]]:
        return self._relationships(
            project,
            {"file_imports_module", "file_depends_on_file"},
            file_id,
            current_only=True,
        )

    def explore_history(
        self, project: Project, entity_id: str | None = None
    ) -> list[dict[str, object]]:
        return self._relationships(
            project,
            self.HISTORY_KINDS,
            entity_id,
            current_only=False,
        )

    def explore_related_code(
        self, project: Project, entity_id: str | None = None
    ) -> list[dict[str, object]]:
        return self._relationships(
            project,
            self.RELATED_KINDS,
            entity_id,
            current_only=True,
        )

    def explore_duplicates(
        self, project: Project, entity_id: str | None = None
    ) -> list[dict[str, object]]:
        return self._relationships(
            project,
            {
                "file_duplicates_file",
                "symbol_duplicates_symbol",
                "chunk_duplicates_chunk",
            },
            entity_id,
            current_only=True,
        )

    def explore_similarity(
        self, project: Project, entity_id: str | None = None
    ) -> list[dict[str, object]]:
        return self._relationships(
            project,
            {"chunk_similar_to_chunk"},
            entity_id,
            current_only=True,
        )

    def contextual_knowledge(self, project: Project) -> dict[str, object]:
        return {
            "project": self.explore_project(project),
            "understanding": self._serialize(project.understanding_result),
            "context": self._serialize(project.context_result),
        }

    def _relationships(
        self, project, kinds, source_identity, *, current_only
    ):
        graph = self._graph(project)
        if graph is None:
            return []
        entities = {item.entity_id: item for item in graph.entities}
        scoped_entity_ids = self._scope_entity_ids(
            graph,
            source_identity,
            kinds,
        )
        result = []
        for relation in graph.relationships:
            if relation.kind not in kinds:
                continue
            if current_only and not relation.is_current:
                continue
            source = entities.get(relation.source_entity_id)
            target = entities.get(relation.target_entity_id)
            if source is None or target is None:
                continue
            identities = (source.source_identity, target.source_identity)
            if (
                scoped_entity_ids is not None
                and relation.source_entity_id not in scoped_entity_ids
                and relation.target_entity_id not in scoped_entity_ids
            ):
                continue
            result.append(
                {
                    "relationship_id": relation.relationship_id,
                    "kind": relation.kind,
                    "source": identities[0],
                    "target": identities[1],
                    "is_current": relation.is_current,
                    "properties": dict(sorted(relation.properties.items())),
                }
            )
        return sorted(
            result,
            key=lambda item: (
                item["kind"], item["source"], item["target"],
                item["relationship_id"],
            ),
        )

    def _scope_entity_ids(self, graph, source_identity, kinds):
        if source_identity is None:
            return None
        scoped = {
            entity.entity_id
            for entity in graph.entities
            if entity.source_identity == source_identity
        }
        if not scoped or not (set(kinds) & self.HISTORY_KINDS):
            return scoped
        ownership_kinds = {
            "file_has_location",
            "file_has_content_state",
        }
        for relationship in graph.relationships:
            if (
                relationship.kind in ownership_kinds
                and relationship.source_entity_id in scoped
            ):
                scoped.add(relationship.target_entity_id)
        return scoped

    def _entity_neighbourhood(self, graph, kind, source_identity):
        matches = sorted(
            (
                item for item in graph.entities
                if item.kind == kind
                and item.source_identity == source_identity
                and item.is_current
            ),
            key=lambda item: item.entity_id,
        )
        if not matches:
            return None
        entity = matches[0]
        relations = self._relationships_for_entity(graph, entity.entity_id)
        return {
            "entity_id": entity.source_identity,
            "kind": entity.kind,
            "properties": dict(sorted(entity.properties.items())),
            "relationships": relations,
        }

    @staticmethod
    def _relationships_for_entity(graph, entity_id):
        entities = {item.entity_id: item for item in graph.entities}
        result = []
        for relation in graph.relationships:
            if entity_id not in {
                relation.source_entity_id,
                relation.target_entity_id,
            }:
                continue
            other_id = (
                relation.target_entity_id
                if relation.source_entity_id == entity_id
                else relation.source_entity_id
            )
            other = entities.get(other_id)
            if other is not None:
                result.append(
                    {
                        "relationship_id": relation.relationship_id,
                        "kind": relation.kind,
                        "related_entity_id": other.source_identity,
                        "is_current": relation.is_current,
                    }
                )
        return sorted(
            result,
            key=lambda item: (
                item["kind"], item["related_entity_id"],
                item["relationship_id"],
            ),
        )

    @staticmethod
    def _counts(items):
        counts: dict[str, int] = {}
        for item in items:
            counts[item.kind] = counts.get(item.kind, 0) + 1
        return dict(sorted(counts.items()))

    @staticmethod
    def _serialize(value):
        if value is None:
            return None
        if hasattr(value, "model_dump"):
            return value.model_dump(mode="json")
        return value

    @staticmethod
    def _graph(project: Project) -> ProjectKnowledgeGraph | None:
        if project.knowledge_state is None:
            return None
        return project.knowledge_state.graph

    @staticmethod
    def _unavailable(project: Project) -> dict[str, object]:
        return {
            "project_id": project.metadata.name,
            "available": False,
        }
