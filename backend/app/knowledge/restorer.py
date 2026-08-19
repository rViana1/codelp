from __future__ import annotations

from core.project import (
    Project,
    ProjectChunkKnowledge,
    ProjectEmbeddingKnowledge,
    ProjectFileKnowledge,
    ProjectKnowledgeState,
    ProjectKnowledgeGraph,
    ProjectKnowledgeGraphEntity,
    ProjectKnowledgeGraphRelationship,
    ProjectRetrievalKnowledge,
    ProjectSymbolKnowledge,
)
from core.project.models import ProjectConfiguration

from app.knowledge.models import PersistentProjectKnowledge


class KnowledgeRestorer:
    """
    Restores persistent knowledge into a Project aggregate.

    Responsible only for translating persisted state
    back into domain state.

    Does not access storage.
    Does not persist data.
    """

    def restore(
        self,
        project: Project,
        knowledge: PersistentProjectKnowledge,
        *,
        report_diagnostic: bool = True,
    ) -> Project:
        """
        Restores compatible knowledge into the project.
        """

        project.configuration = ProjectConfiguration(
            follow_symlinks=knowledge.configuration.follow_symlinks,
            ignore_hidden=knowledge.configuration.ignore_hidden,
            max_file_size_bytes=knowledge.configuration.max_file_size_bytes,
            ignored_directories=set(
                knowledge.configuration.ignored_directories
            ),
            ignored_extensions=set(
                knowledge.configuration.ignored_extensions
            ),
        )

        project.knowledge_state = ProjectKnowledgeState(
            files=[
                ProjectFileKnowledge(
                    file_id=file.file_id,
                    path=(
                        next(
                            (
                                location.path
                                for location in file.locations
                                if location.is_current
                            ),
                            "",
                        )
                    ),
                    content_hash=(
                        next(
                            (
                                fingerprint.content_hash
                                for fingerprint in file.fingerprints
                                if fingerprint.is_current
                            ),
                            "",
                        )
                    ),
                )
                for file in knowledge.files
                if any(
                    location.is_current
                    for location in file.locations
                )
            ],
            symbols=[
                ProjectSymbolKnowledge(
                    symbol_id=symbol.symbol_id,
                    file_id=symbol.file_id,
                    name=symbol.name,
                    symbol_type=symbol.symbol_type,
                )
                for symbol in knowledge.symbols
            ],
            chunks=[
                ProjectChunkKnowledge(
                    chunk_id=chunk.chunk_id,
                    symbol_id=chunk.symbol_id,
                    content_hash=chunk.content_hash,
                )
                for chunk in knowledge.chunks
            ],
            embeddings=[
                ProjectEmbeddingKnowledge(
                    chunk_id=embedding.chunk_id,
                    provider=embedding.provider,
                    embedding_hash=embedding.embedding_hash,
                )
                for embedding in knowledge.embeddings
            ],
            retrieval=[
                ProjectRetrievalKnowledge(
                    chunk_id=item.chunk_id,
                    query_hash=item.query_hash,
                    score=item.score,
                )
                for item in knowledge.retrieval
            ],
            graph=(
                ProjectKnowledgeGraph(
                    graph_id=knowledge.graph.graph_id,
                    project_id=knowledge.graph.project_id,
                    entities=[
                        ProjectKnowledgeGraphEntity(
                            entity_id=entity.entity_id,
                            kind=entity.kind.value,
                            source_identity=entity.source_identity,
                            first_observed_at=entity.first_observed_at,
                            last_observed_at=entity.last_observed_at,
                            is_current=entity.is_current,
                            properties=dict(entity.properties),
                        )
                        for entity in knowledge.graph.entities
                    ],
                    relationships=[
                        ProjectKnowledgeGraphRelationship(
                            relationship_id=relationship.relationship_id,
                            kind=relationship.kind.value,
                            source_entity_id=relationship.source_entity_id,
                            target_entity_id=relationship.target_entity_id,
                            first_observed_at=(
                                relationship.first_observed_at
                            ),
                            last_observed_at=relationship.last_observed_at,
                            is_current=relationship.is_current,
                            properties=dict(relationship.properties),
                        )
                        for relationship in knowledge.graph.relationships
                    ],
                )
                if knowledge.graph is not None
                else None
            ),
        )

        if report_diagnostic:
            project.diagnostics.append(
                f"Restored knowledge for project "
                f"{knowledge.metadata.project_id}"
            )

        return project
