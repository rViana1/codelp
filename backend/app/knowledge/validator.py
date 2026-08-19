from __future__ import annotations

from pathlib import PurePosixPath

from app.knowledge.models import PersistentProjectKnowledge
from app.knowledge.identity import deterministic_identity
from app.knowledge.schema import is_supported_version

from app.knowledge.errors import KnowledgeValidationError
from app.knowledge.validation_codes import (
    KNOWLEDGE_UNSUPPORTED_VERSION,
)


class KnowledgeValidator:
    """
    Validates persisted project knowledge consistency.
    """


    def validate(
        self,
        knowledge: PersistentProjectKnowledge,
    ) -> None:
        """
        Validates knowledge invariants.
        """


        self._validate_schema_version(
            knowledge
        )

        self._validate_metadata(
            knowledge
        )

        self._validate_identity_references(
            knowledge
        )

        self._validate_required_fields(
            knowledge
        )

        self._validate_graph(
            knowledge
        )


    def _validate_schema_version(
        self,
        knowledge: PersistentProjectKnowledge,
    ) -> None:

        if not is_supported_version(
            knowledge.metadata.version
        ):
            raise KnowledgeValidationError(
                KNOWLEDGE_UNSUPPORTED_VERSION,
                "Unsupported knowledge version",
            )


    def _validate_metadata(
        self,
        knowledge: PersistentProjectKnowledge,
    ) -> None:

        if not knowledge.metadata.project_id:
            raise ValueError(
                "Knowledge requires project_id"
            )


    def _validate_identity_references(
        self,
        knowledge: PersistentProjectKnowledge,
    ) -> None:

        file_ids = {
            file.file_id
            for file in knowledge.files
        }


        symbol_ids = {
            symbol.symbol_id
            for symbol in knowledge.symbols
        }


        chunk_ids = {
            chunk.chunk_id
            for chunk in knowledge.chunks
        }


        if len(file_ids) != len(knowledge.files):
            raise ValueError(
                "Duplicate file identities detected"
            )


        if len(symbol_ids) != len(knowledge.symbols):
            raise ValueError(
                "Duplicate symbol identities detected"
            )


        if len(chunk_ids) != len(knowledge.chunks):
            raise ValueError(
                "Duplicate chunk identities detected"
            )


        for symbol in knowledge.symbols:
            if symbol.file_id not in file_ids:
                raise ValueError(
                    "Symbol references unknown file identity"
                )


        for chunk in knowledge.chunks:
            if chunk.symbol_id not in symbol_ids:
                raise ValueError(
                    "Chunk references unknown symbol identity"
                )


        for embedding in knowledge.embeddings:
            if embedding.chunk_id not in chunk_ids:
                raise ValueError(
                    "Embedding references unknown chunk identity"
                )

        embedding_keys = {
            (embedding.chunk_id, embedding.provider)
            for embedding in knowledge.embeddings
        }
        if len(embedding_keys) != len(knowledge.embeddings):
            raise ValueError(
                "Duplicate embedding identities detected"
            )

        retrieval_keys = {
            (item.chunk_id, item.query_hash)
            for item in knowledge.retrieval
        }
        if len(retrieval_keys) != len(knowledge.retrieval):
            raise ValueError(
                "Duplicate retrieval identities detected"
            )


        for retrieval in knowledge.retrieval:
            if retrieval.chunk_id not in chunk_ids:
                raise ValueError(
                    "Retrieval references unknown chunk identity"
                )


    def _validate_required_fields(
        self,
        knowledge: PersistentProjectKnowledge,
    ) -> None:


        for file in knowledge.files:

            if not file.file_id:
                raise ValueError(
                    "File requires identity"
                )

            if not file.locations:
                raise ValueError(
                    "File requires location history"
                )

            if not file.fingerprints:
                raise ValueError(
                    "File requires fingerprint history"
                )

            current_locations = [
                location
                for location in file.locations
                if location.is_current
            ]
            current_fingerprints = [
                fingerprint
                for fingerprint in file.fingerprints
                if fingerprint.is_current
            ]

            if len(current_locations) > 1:
                raise ValueError(
                    "File has multiple current locations"
                )

            if len(current_fingerprints) > 1:
                raise ValueError(
                    "File has multiple current fingerprints"
                )

            if bool(current_locations) != bool(
                current_fingerprints
            ):
                raise ValueError(
                    "Current file state is inconsistent"
                )

            paths = set()
            for location in file.locations:
                if not location.path:
                    raise ValueError(
                        "File location requires path"
                    )
                canonical_path = PurePosixPath(location.path)
                if (
                    canonical_path.is_absolute()
                    or "\\" in location.path
                    or ".." in canonical_path.parts
                ):
                    raise ValueError(
                        "File location must be project-relative POSIX path"
                    )
                if location.path in paths:
                    raise ValueError(
                        "Duplicate file location detected"
                    )
                if location.last_seen < location.first_seen:
                    raise ValueError(
                        "File location has invalid timestamps"
                    )
                paths.add(location.path)

            fingerprints = set()
            for fingerprint in file.fingerprints:
                if not fingerprint.content_hash:
                    raise ValueError(
                        "File fingerprint requires content hash"
                    )
                if fingerprint.size_bytes < 0:
                    raise ValueError(
                        "File fingerprint size cannot be negative"
                    )
                if fingerprint.content_hash in fingerprints:
                    raise ValueError(
                        "Duplicate file fingerprint detected"
                    )
                if fingerprint.last_seen < fingerprint.generated_at:
                    raise ValueError(
                        "File fingerprint has invalid timestamps"
                    )
                fingerprints.add(fingerprint.content_hash)


        for symbol in knowledge.symbols:

            if not symbol.symbol_id:
                raise ValueError(
                    "Symbol requires identity"
                )

            if not symbol.name:
                raise ValueError(
                    "Symbol requires name"
                )


        for chunk in knowledge.chunks:

            if not chunk.chunk_id:
                raise ValueError(
                    "Chunk requires identity"
                )

            if not chunk.content_hash:
                raise ValueError(
                    "Chunk requires content hash"
                )


        for embedding in knowledge.embeddings:

            if not embedding.chunk_id:
                raise ValueError(
                    "Embedding requires chunk identity"
                )

            if not embedding.provider:
                raise ValueError(
                    "Embedding requires provider"
                )

            if not embedding.embedding_hash:
                raise ValueError(
                    "Embedding requires hash"
                )


        for retrieval in knowledge.retrieval:

            if not retrieval.chunk_id:
                raise ValueError(
                    "Retrieval requires chunk identity"
                )

            if not retrieval.query_hash:
                raise ValueError(
                    "Retrieval requires query hash"
                )

            if retrieval.score < 0:
                raise ValueError(
                    "Retrieval score cannot be negative"
                )

        import_ids = set()
        for reference in knowledge.imports:
            if not reference.import_id:
                raise ValueError("Import reference requires identity")
            if reference.import_id in import_ids:
                raise ValueError("Duplicate import identities detected")
            if reference.source_file_id not in {
                file.file_id for file in knowledge.files
            }:
                raise ValueError("Import references unknown source file")
            if (
                reference.target_file_id is not None
                and reference.target_file_id
                not in {file.file_id for file in knowledge.files}
            ):
                raise ValueError("Import references unknown target file")
            if not reference.imported_module:
                raise ValueError("Import reference requires module")
            expected_import_id = deterministic_identity(
                knowledge.metadata.project_id,
                "import",
                reference.source_file_id,
                reference.imported_module,
            )
            if reference.import_id != expected_import_id:
                raise ValueError("Import identity is not deterministic")
            import_ids.add(reference.import_id)


    def validate_project_identity(
        self,
        project_id: str,
        knowledge: PersistentProjectKnowledge,
    ) -> None:

        if knowledge.metadata.project_id != project_id:
            raise ValueError(
                "Knowledge belongs to a different project"
            )

    def _validate_graph(
        self,
        knowledge: PersistentProjectKnowledge,
    ) -> None:
        graph = knowledge.graph
        if graph is None:
            return
        if not graph.graph_id:
            raise ValueError("Knowledge graph requires identity")
        if graph.project_id != knowledge.metadata.project_id:
            raise ValueError("Knowledge graph belongs to a different project")
        expected_graph_id = deterministic_identity(
            graph.project_id,
            "knowledge_graph",
        )
        if graph.graph_id != expected_graph_id:
            raise ValueError("Knowledge graph identity is not deterministic")

        entity_ids = [entity.entity_id for entity in graph.entities]
        if len(entity_ids) != len(set(entity_ids)):
            raise ValueError("Duplicate graph entity identities detected")
        entity_keys = [
            (entity.kind, entity.source_identity)
            for entity in graph.entities
        ]
        if len(entity_keys) != len(set(entity_keys)):
            raise ValueError("Duplicate graph source entities detected")

        entities_by_id = {
            entity.entity_id: entity
            for entity in graph.entities
        }
        for entity in graph.entities:
            if not entity.entity_id or not entity.source_identity:
                raise ValueError("Graph entity requires identity")
            expected_entity_id = deterministic_identity(
                graph.project_id,
                "graph_entity",
                entity.kind.value,
                entity.source_identity,
            )
            if entity.entity_id != expected_entity_id:
                raise ValueError("Graph entity identity is not deterministic")
            if (
                entity.first_observed_at is not None
                and entity.last_observed_at is not None
                and entity.last_observed_at < entity.first_observed_at
            ):
                raise ValueError("Graph entity has invalid observation window")

        relationship_ids = [
            relationship.relationship_id
            for relationship in graph.relationships
        ]
        if len(relationship_ids) != len(set(relationship_ids)):
            raise ValueError(
                "Duplicate graph relationship identities detected"
            )
        relationship_keys = [
            (
                relationship.kind,
                relationship.source_entity_id,
                relationship.target_entity_id,
            )
            for relationship in graph.relationships
        ]
        if len(relationship_keys) != len(set(relationship_keys)):
            raise ValueError("Duplicate graph relationships detected")

        for relationship in graph.relationships:
            if not relationship.relationship_id:
                raise ValueError("Graph relationship requires identity")
            expected_relationship_id = deterministic_identity(
                graph.project_id,
                "graph_relationship",
                relationship.kind.value,
                relationship.source_entity_id,
                relationship.target_entity_id,
            )
            if relationship.relationship_id != expected_relationship_id:
                raise ValueError(
                    "Graph relationship identity is not deterministic"
                )
            if relationship.source_entity_id not in entities_by_id:
                raise ValueError("Graph relationship has unknown source")
            if relationship.target_entity_id not in entities_by_id:
                raise ValueError("Graph relationship has unknown target")
            if relationship.source_entity_id == relationship.target_entity_id:
                raise ValueError("Graph relationship cannot reference itself")
            if (
                relationship.first_observed_at is not None
                and relationship.last_observed_at is not None
                and relationship.last_observed_at
                < relationship.first_observed_at
            ):
                raise ValueError(
                    "Graph relationship has invalid observation window"
                )
            if relationship.is_current:
                if not entities_by_id[relationship.source_entity_id].is_current:
                    raise ValueError(
                        "Current graph relationship has historical source"
                    )
                if not entities_by_id[relationship.target_entity_id].is_current:
                    raise ValueError(
                        "Current graph relationship has historical target"
                    )
