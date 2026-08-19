"""Deterministic persistent knowledge graph projection."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import PurePosixPath

from app.knowledge.identity import deterministic_identity
from app.knowledge.models import (
    KnowledgeGraphEntityKind,
    KnowledgeGraphRelationshipKind,
    PersistentKnowledgeGraph,
    PersistentKnowledgeGraphEntity,
    PersistentKnowledgeGraphRelationship,
    PersistentProjectKnowledge,
)


class KnowledgeGraphBuilder:
    """Project persistent knowledge into a stable, temporal graph.

    The graph never invents a second identity for source entities. Its node
    identities are deterministic projections of the persistent identities
    already owned by the Knowledge layer. Previous nodes and relationships
    are retained as inactive history when their source entities disappear.
    """

    def build(
        self,
        knowledge: PersistentProjectKnowledge,
        previous: PersistentKnowledgeGraph | None = None,
    ) -> PersistentKnowledgeGraph:
        project_id = knowledge.metadata.project_id
        observed_at = knowledge.metadata.updated_at
        entities: dict[str, PersistentKnowledgeGraphEntity] = {}
        relationships: dict[
            str,
            PersistentKnowledgeGraphRelationship,
        ] = {}

        project = self._entity(
            project_id=project_id,
            kind=KnowledgeGraphEntityKind.PROJECT,
            source_identity=project_id,
            first_observed_at=knowledge.metadata.created_at,
            last_observed_at=observed_at,
        )
        entities[project.entity_id] = project

        file_nodes = {}
        for file in knowledge.files:
            timestamps = [
                timestamp
                for location in file.locations
                for timestamp in (location.first_seen, location.last_seen)
            ] + [
                timestamp
                for fingerprint in file.fingerprints
                for timestamp in (
                    fingerprint.generated_at,
                    fingerprint.last_seen,
                )
            ]
            current_location = next(
                (
                    location.path
                    for location in file.locations
                    if location.is_current
                ),
                "",
            )
            current_fingerprint = next(
                (
                    fingerprint.content_hash
                    for fingerprint in file.fingerprints
                    if fingerprint.is_current
                ),
                "",
            )
            is_current = bool(current_location)
            file_node = self._entity(
                project_id=project_id,
                kind=KnowledgeGraphEntityKind.FILE,
                source_identity=file.file_id,
                first_observed_at=min(timestamps) if timestamps else observed_at,
                last_observed_at=max(timestamps) if timestamps else observed_at,
                is_current=is_current,
                properties={
                    "current_path": current_location,
                    "current_content_hash": current_fingerprint,
                },
            )
            entities[file_node.entity_id] = file_node
            file_nodes[file.file_id] = file_node
            self._add_relationship(
                relationships,
                project_id=project_id,
                kind=KnowledgeGraphRelationshipKind.PROJECT_CONTAINS_FILE,
                source=project,
                target=file_node,
                first_observed_at=file_node.first_observed_at,
                last_observed_at=file_node.last_observed_at,
                is_current=is_current,
            )

            location_nodes = []
            for location in file.locations:
                location_node = self._entity(
                    project_id=project_id,
                    kind=KnowledgeGraphEntityKind.FILE_LOCATION,
                    source_identity=self._composite_identity(
                        file.file_id,
                        location.path,
                    ),
                    first_observed_at=location.first_seen,
                    last_observed_at=location.last_seen,
                    is_current=location.is_current,
                    properties={"path": location.path},
                )
                entities[location_node.entity_id] = location_node
                location_nodes.append(location_node)
                self._add_relationship(
                    relationships,
                    project_id=project_id,
                    kind=KnowledgeGraphRelationshipKind.FILE_HAS_LOCATION,
                    source=file_node,
                    target=location_node,
                    first_observed_at=location.first_seen,
                    last_observed_at=location.last_seen,
                    is_current=location.is_current,
                )
            for before, after in zip(
                sorted(
                    location_nodes,
                    key=lambda item: (
                        item.first_observed_at,
                        item.source_identity,
                    ),
                ),
                sorted(
                    location_nodes,
                    key=lambda item: (
                        item.first_observed_at,
                        item.source_identity,
                    ),
                )[1:],
            ):
                self._add_relationship(
                    relationships,
                    project_id=project_id,
                    kind=self._location_evolution_kind(before, after),
                    source=before,
                    target=after,
                    first_observed_at=before.first_observed_at,
                    last_observed_at=after.last_observed_at,
                    is_current=False,
                )

            content_nodes = []
            for fingerprint in file.fingerprints:
                fingerprint_node = self._entity(
                    project_id=project_id,
                    kind=KnowledgeGraphEntityKind.FILE_CONTENT_STATE,
                    source_identity=self._composite_identity(
                        file.file_id,
                        fingerprint.content_hash,
                    ),
                    first_observed_at=fingerprint.generated_at,
                    last_observed_at=fingerprint.last_seen,
                    is_current=fingerprint.is_current,
                    properties={
                        "content_hash": fingerprint.content_hash,
                        "size_bytes": str(fingerprint.size_bytes),
                    },
                )
                entities[fingerprint_node.entity_id] = fingerprint_node
                content_nodes.append(fingerprint_node)
                self._add_relationship(
                    relationships,
                    project_id=project_id,
                    kind=(
                        KnowledgeGraphRelationshipKind.FILE_HAS_CONTENT_STATE
                    ),
                    source=file_node,
                    target=fingerprint_node,
                    first_observed_at=fingerprint.generated_at,
                    last_observed_at=fingerprint.last_seen,
                    is_current=fingerprint.is_current,
                )
            ordered_content = sorted(
                content_nodes,
                key=lambda item: (
                    item.first_observed_at,
                    item.source_identity,
                ),
            )
            for before, after in zip(
                ordered_content,
                ordered_content[1:],
            ):
                self._add_relationship(
                    relationships,
                    project_id=project_id,
                    kind=(
                        KnowledgeGraphRelationshipKind.CONTENT_STATE_EVOLVED_TO
                    ),
                    source=before,
                    target=after,
                    first_observed_at=before.first_observed_at,
                    last_observed_at=after.last_observed_at,
                    is_current=False,
                )

            current_location_node = next(
                (item for item in location_nodes if item.is_current),
                None,
            )
            previous_location_node = self._previous_current_target(
                previous,
                file_node.entity_id,
                KnowledgeGraphRelationshipKind.FILE_HAS_LOCATION,
            )
            if (
                current_location_node is not None
                and previous_location_node is not None
                and current_location_node.entity_id
                != previous_location_node.entity_id
            ):
                self._add_relationship(
                    relationships,
                    project_id=project_id,
                    kind=self._location_evolution_kind(
                        previous_location_node,
                        current_location_node,
                    ),
                    source=previous_location_node,
                    target=current_location_node,
                    first_observed_at=observed_at,
                    last_observed_at=observed_at,
                    is_current=False,
                )

            current_content_node = next(
                (item for item in content_nodes if item.is_current),
                None,
            )
            previous_content_node = self._previous_current_target(
                previous,
                file_node.entity_id,
                KnowledgeGraphRelationshipKind.FILE_HAS_CONTENT_STATE,
            )
            if (
                current_content_node is not None
                and previous_content_node is not None
                and current_content_node.entity_id
                != previous_content_node.entity_id
            ):
                self._add_relationship(
                    relationships,
                    project_id=project_id,
                    kind=(
                        KnowledgeGraphRelationshipKind.CONTENT_STATE_EVOLVED_TO
                    ),
                    source=previous_content_node,
                    target=current_content_node,
                    first_observed_at=observed_at,
                    last_observed_at=observed_at,
                    is_current=False,
                )

        symbol_nodes = {}
        for symbol in knowledge.symbols:
            symbol_node = self._entity(
                project_id=project_id,
                kind=KnowledgeGraphEntityKind.SYMBOL,
                source_identity=symbol.symbol_id,
                first_observed_at=observed_at,
                last_observed_at=observed_at,
                properties={
                    "name": symbol.name,
                    "symbol_type": symbol.symbol_type,
                },
            )
            entities[symbol_node.entity_id] = symbol_node
            symbol_nodes[symbol.symbol_id] = symbol_node
            file_node = file_nodes.get(symbol.file_id)
            if file_node is not None:
                self._add_relationship(
                    relationships,
                    project_id=project_id,
                    kind=KnowledgeGraphRelationshipKind.FILE_DECLARES_SYMBOL,
                    source=file_node,
                    target=symbol_node,
                    first_observed_at=observed_at,
                    last_observed_at=observed_at,
                )

        chunk_nodes = {}
        for chunk in knowledge.chunks:
            chunk_node = self._entity(
                project_id=project_id,
                kind=KnowledgeGraphEntityKind.CHUNK,
                source_identity=chunk.chunk_id,
                first_observed_at=observed_at,
                last_observed_at=observed_at,
                properties={"content_hash": chunk.content_hash},
            )
            entities[chunk_node.entity_id] = chunk_node
            chunk_nodes[chunk.chunk_id] = chunk_node
            symbol_node = symbol_nodes.get(chunk.symbol_id)
            if symbol_node is not None:
                self._add_relationship(
                    relationships,
                    project_id=project_id,
                    kind=KnowledgeGraphRelationshipKind.SYMBOL_HAS_CHUNK,
                    source=symbol_node,
                    target=chunk_node,
                    first_observed_at=observed_at,
                    last_observed_at=observed_at,
                )

        for embedding in knowledge.embeddings:
            embedding_node = self._entity(
                project_id=project_id,
                kind=KnowledgeGraphEntityKind.EMBEDDING,
                source_identity=self._composite_identity(
                    embedding.chunk_id,
                    embedding.provider,
                ),
                first_observed_at=observed_at,
                last_observed_at=observed_at,
                properties={
                    "provider": embedding.provider,
                    "embedding_hash": embedding.embedding_hash,
                },
            )
            entities[embedding_node.entity_id] = embedding_node
            chunk_node = chunk_nodes.get(embedding.chunk_id)
            if chunk_node is not None:
                self._add_relationship(
                    relationships,
                    project_id=project_id,
                    kind=KnowledgeGraphRelationshipKind.CHUNK_HAS_EMBEDDING,
                    source=chunk_node,
                    target=embedding_node,
                    first_observed_at=observed_at,
                    last_observed_at=observed_at,
                )

        for retrieval in knowledge.retrieval:
            retrieval_node = self._entity(
                project_id=project_id,
                kind=KnowledgeGraphEntityKind.RETRIEVAL,
                source_identity=self._composite_identity(
                    retrieval.chunk_id,
                    retrieval.query_hash,
                ),
                first_observed_at=observed_at,
                last_observed_at=observed_at,
                properties={
                    "query_hash": retrieval.query_hash,
                    "score": format(retrieval.score, ".17g"),
                },
            )
            entities[retrieval_node.entity_id] = retrieval_node
            chunk_node = chunk_nodes.get(retrieval.chunk_id)
            if chunk_node is not None:
                self._add_relationship(
                    relationships,
                    project_id=project_id,
                    kind=KnowledgeGraphRelationshipKind.CHUNK_HAS_RETRIEVAL,
                    source=chunk_node,
                    target=retrieval_node,
                    first_observed_at=observed_at,
                    last_observed_at=observed_at,
                )

        module_nodes = {}
        for reference in knowledge.imports:
            module_node = module_nodes.get(reference.imported_module)
            if module_node is None:
                module_node = self._entity(
                    project_id=project_id,
                    kind=KnowledgeGraphEntityKind.MODULE,
                    source_identity=reference.imported_module,
                    first_observed_at=observed_at,
                    last_observed_at=observed_at,
                    properties={"name": reference.imported_module},
                )
                module_nodes[reference.imported_module] = module_node
                entities[module_node.entity_id] = module_node
            source_file = file_nodes.get(reference.source_file_id)
            if source_file is None:
                continue
            self._add_relationship(
                relationships,
                project_id=project_id,
                kind=KnowledgeGraphRelationshipKind.FILE_IMPORTS_MODULE,
                source=source_file,
                target=module_node,
                first_observed_at=observed_at,
                last_observed_at=observed_at,
                properties={"import_id": reference.import_id},
            )
            target_file = file_nodes.get(reference.target_file_id or "")
            if target_file is not None and target_file.entity_id != source_file.entity_id:
                self._add_relationship(
                    relationships,
                    project_id=project_id,
                    kind=KnowledgeGraphRelationshipKind.FILE_DEPENDS_ON_FILE,
                    source=source_file,
                    target=target_file,
                    first_observed_at=observed_at,
                    last_observed_at=observed_at,
                    properties={"module": reference.imported_module},
                )

        current_hash_groups = {}
        for file in knowledge.files:
            current_hash = next(
                (
                    item.content_hash
                    for item in file.fingerprints
                    if item.is_current
                ),
                None,
            )
            if current_hash is not None and file.file_id in file_nodes:
                current_hash_groups.setdefault(current_hash, []).append(
                    file_nodes[file.file_id]
                )
        self._add_group_relationships(
            relationships,
            project_id=project_id,
            kind=KnowledgeGraphRelationshipKind.FILE_DUPLICATES_FILE,
            groups=current_hash_groups.values(),
            observed_at=observed_at,
        )

        symbol_groups = {}
        for symbol in knowledge.symbols:
            symbol_groups.setdefault(
                (symbol.symbol_type, symbol.name),
                [],
            ).append((symbol.file_id, symbol_nodes[symbol.symbol_id]))
        for group in symbol_groups.values():
            ordered = sorted(group, key=lambda item: item[1].entity_id)
            for index, (source_file_id, source) in enumerate(ordered):
                for target_file_id, target in ordered[index + 1:]:
                    if source_file_id == target_file_id:
                        continue
                    self._add_relationship(
                        relationships,
                        project_id=project_id,
                        kind=(
                            KnowledgeGraphRelationshipKind.SYMBOL_DUPLICATES_SYMBOL
                        ),
                        source=source,
                        target=target,
                        first_observed_at=observed_at,
                        last_observed_at=observed_at,
                    )

        chunk_hash_groups = {}
        for chunk in knowledge.chunks:
            chunk_hash_groups.setdefault(chunk.content_hash, []).append(
                chunk_nodes[chunk.chunk_id]
            )
        self._add_group_relationships(
            relationships,
            project_id=project_id,
            kind=KnowledgeGraphRelationshipKind.CHUNK_DUPLICATES_CHUNK,
            groups=chunk_hash_groups.values(),
            observed_at=observed_at,
        )

        for index, left in enumerate(knowledge.chunks):
            for right in knowledge.chunks[index + 1:]:
                similarity = self._fingerprint_similarity(
                    left.structural_fingerprint,
                    right.structural_fingerprint,
                )
                if similarity < 0.6:
                    continue
                source, target = sorted(
                    (chunk_nodes[left.chunk_id], chunk_nodes[right.chunk_id]),
                    key=lambda item: item.entity_id,
                )
                self._add_relationship(
                    relationships,
                    project_id=project_id,
                    kind=(
                        KnowledgeGraphRelationshipKind.CHUNK_SIMILAR_TO_CHUNK
                    ),
                    source=source,
                    target=target,
                    first_observed_at=observed_at,
                    last_observed_at=observed_at,
                    properties={"score": format(similarity, ".17g")},
                )

        entities = self._merge_historical_entities(previous, entities)
        relationships = self._merge_historical_relationships(
            previous,
            relationships,
        )
        return PersistentKnowledgeGraph(
            graph_id=deterministic_identity(project_id, "knowledge_graph"),
            project_id=project_id,
            entities=sorted(entities.values(), key=lambda item: item.entity_id),
            relationships=sorted(
                relationships.values(),
                key=lambda item: item.relationship_id,
            ),
        )

    @staticmethod
    def _entity(
        *,
        project_id: str,
        kind: KnowledgeGraphEntityKind,
        source_identity: str,
        first_observed_at: datetime | None,
        last_observed_at: datetime | None,
        is_current: bool = True,
        properties: dict[str, str] | None = None,
    ) -> PersistentKnowledgeGraphEntity:
        return PersistentKnowledgeGraphEntity(
            entity_id=deterministic_identity(
                project_id,
                "graph_entity",
                kind.value,
                source_identity,
            ),
            kind=kind,
            source_identity=source_identity,
            first_observed_at=first_observed_at,
            last_observed_at=last_observed_at,
            is_current=is_current,
            properties=dict(sorted((properties or {}).items())),
        )

    @staticmethod
    def _composite_identity(*parts: str) -> str:
        """Encode composite source identities without delimiter ambiguity."""
        return json.dumps(
            parts,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    @staticmethod
    def _add_relationship(
        relationships: dict[str, PersistentKnowledgeGraphRelationship],
        *,
        project_id: str,
        kind: KnowledgeGraphRelationshipKind,
        source: PersistentKnowledgeGraphEntity,
        target: PersistentKnowledgeGraphEntity,
        first_observed_at: datetime | None,
        last_observed_at: datetime | None,
        is_current: bool = True,
        properties: dict[str, str] | None = None,
    ) -> None:
        relationship_id = deterministic_identity(
            project_id,
            "graph_relationship",
            kind.value,
            source.entity_id,
            target.entity_id,
        )
        relationships[relationship_id] = PersistentKnowledgeGraphRelationship(
            relationship_id=relationship_id,
            kind=kind,
            source_entity_id=source.entity_id,
            target_entity_id=target.entity_id,
            first_observed_at=first_observed_at,
            last_observed_at=last_observed_at,
            is_current=is_current,
            properties=dict(sorted((properties or {}).items())),
        )

    @staticmethod
    def _add_group_relationships(
        relationships: dict[str, PersistentKnowledgeGraphRelationship],
        *,
        project_id: str,
        kind: KnowledgeGraphRelationshipKind,
        groups,
        observed_at: datetime,
    ) -> None:
        for group in groups:
            ordered = sorted(group, key=lambda item: item.entity_id)
            for index, source in enumerate(ordered):
                for target in ordered[index + 1:]:
                    KnowledgeGraphBuilder._add_relationship(
                        relationships,
                        project_id=project_id,
                        kind=kind,
                        source=source,
                        target=target,
                        first_observed_at=observed_at,
                        last_observed_at=observed_at,
                    )

    @staticmethod
    def _fingerprint_similarity(
        left: tuple[str, ...],
        right: tuple[str, ...],
    ) -> float:
        left_set = set(left)
        right_set = set(right)
        if not left_set or not right_set:
            return 0.0
        return len(left_set & right_set) / len(left_set | right_set)

    @staticmethod
    def _location_evolution_kind(
        before: PersistentKnowledgeGraphEntity,
        after: PersistentKnowledgeGraphEntity,
    ) -> KnowledgeGraphRelationshipKind:
        previous = PurePosixPath(before.properties["path"])
        current = PurePosixPath(after.properties["path"])
        if previous.name == current.name:
            return KnowledgeGraphRelationshipKind.LOCATION_MOVED_TO
        if previous.parent == current.parent:
            return KnowledgeGraphRelationshipKind.LOCATION_RENAMED_TO
        return (
            KnowledgeGraphRelationshipKind.LOCATION_MOVED_AND_RENAMED_TO
        )

    @staticmethod
    def _previous_current_target(
        graph: PersistentKnowledgeGraph | None,
        source_entity_id: str,
        kind: KnowledgeGraphRelationshipKind,
    ) -> PersistentKnowledgeGraphEntity | None:
        if graph is None:
            return None
        target_id = next(
            (
                relationship.target_entity_id
                for relationship in graph.relationships
                if relationship.kind == kind
                and relationship.source_entity_id == source_entity_id
                and relationship.is_current
            ),
            None,
        )
        if target_id is None:
            return None
        return next(
            (
                entity
                for entity in graph.entities
                if entity.entity_id == target_id
            ),
            None,
        )

    @staticmethod
    def _merge_historical_entities(
        previous: PersistentKnowledgeGraph | None,
        current: dict[str, PersistentKnowledgeGraphEntity],
    ) -> dict[str, PersistentKnowledgeGraphEntity]:
        if previous is None:
            return current
        for before in previous.entities:
            after = current.get(before.entity_id)
            if after is None:
                current[before.entity_id] = before.model_copy(
                    update={"is_current": False},
                    deep=True,
                )
                continue
            current[before.entity_id] = after.model_copy(
                update={
                    "first_observed_at": KnowledgeGraphBuilder._earliest(
                        before.first_observed_at,
                        after.first_observed_at,
                    ),
                    "last_observed_at": KnowledgeGraphBuilder._latest(
                        before.last_observed_at,
                        after.last_observed_at,
                    ),
                },
                deep=True,
            )
        return current

    @staticmethod
    def _merge_historical_relationships(
        previous: PersistentKnowledgeGraph | None,
        current: dict[str, PersistentKnowledgeGraphRelationship],
    ) -> dict[str, PersistentKnowledgeGraphRelationship]:
        if previous is None:
            return current
        for before in previous.relationships:
            after = current.get(before.relationship_id)
            if after is None:
                current[before.relationship_id] = before.model_copy(
                    update={"is_current": False},
                    deep=True,
                )
                continue
            current[before.relationship_id] = after.model_copy(
                update={
                    "first_observed_at": KnowledgeGraphBuilder._earliest(
                        before.first_observed_at,
                        after.first_observed_at,
                    ),
                    "last_observed_at": KnowledgeGraphBuilder._latest(
                        before.last_observed_at,
                        after.last_observed_at,
                    ),
                },
                deep=True,
            )
        return current

    @staticmethod
    def _earliest(
        first: datetime | None,
        second: datetime | None,
    ) -> datetime | None:
        values = [value for value in (first, second) if value is not None]
        return min(values) if values else None

    @staticmethod
    def _latest(
        first: datetime | None,
        second: datetime | None,
    ) -> datetime | None:
        values = [value for value in (first, second) if value is not None]
        return max(values) if values else None
