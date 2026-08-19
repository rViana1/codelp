from __future__ import annotations

from app.knowledge.models import (
    PersistentFileIdentity,
    PersistentKnowledgeGraph,
    PersistentKnowledgeGraphEntity,
    PersistentKnowledgeGraphRelationship,
    PersistentProjectKnowledge,
)


class KnowledgeNormalizer:
    """
    Creates deterministic representations
    of project knowledge snapshots.

    Does not mutate the original snapshot.
    """

    def normalize(
        self,
        knowledge: PersistentProjectKnowledge,
    ) -> PersistentProjectKnowledge:
        """
        Returns a deterministically ordered copy
        of project knowledge.
        """

        return PersistentProjectKnowledge(
            metadata=knowledge.metadata,
            configuration=knowledge.configuration,
            files=sorted(
                (
                    PersistentFileIdentity(
                        file_id=file.file_id,
                        locations=sorted(
                            file.locations,
                            key=lambda location: (
                                location.first_seen,
                                location.path,
                            ),
                        ),
                        fingerprints=sorted(
                            file.fingerprints,
                            key=lambda fingerprint: (
                                fingerprint.generated_at,
                                fingerprint.content_hash,
                            ),
                        ),
                    )
                    for file in knowledge.files
                ),
                key=lambda item: item.file_id,
            ),
            symbols=sorted(
                knowledge.symbols,
                key=lambda item: item.symbol_id,
            ),
            chunks=sorted(
                knowledge.chunks,
                key=lambda item: item.chunk_id,
            ),
            embeddings=sorted(
                knowledge.embeddings,
                key=lambda item: (
                    item.chunk_id,
                    item.provider,
                ),
            ),
            retrieval=sorted(
                knowledge.retrieval,
                key=lambda item: (
                    item.chunk_id,
                    item.query_hash,
                ),
            ),
            imports=sorted(
                knowledge.imports,
                key=lambda item: item.import_id,
            ),
            graph=self._normalize_graph(knowledge.graph),
        )

    @staticmethod
    def _normalize_graph(
        graph: PersistentKnowledgeGraph | None,
    ) -> PersistentKnowledgeGraph | None:
        if graph is None:
            return None
        return PersistentKnowledgeGraph(
            graph_id=graph.graph_id,
            project_id=graph.project_id,
            entities=sorted(
                (
                    PersistentKnowledgeGraphEntity(
                        **entity.model_dump(exclude={"properties"}),
                        properties=dict(sorted(entity.properties.items())),
                    )
                    for entity in graph.entities
                ),
                key=lambda item: item.entity_id,
            ),
            relationships=sorted(
                (
                    PersistentKnowledgeGraphRelationship(
                        **relationship.model_dump(exclude={"properties"}),
                        properties=dict(
                            sorted(relationship.properties.items())
                        ),
                    )
                    for relationship in graph.relationships
                ),
                key=lambda item: item.relationship_id,
            ),
        )
