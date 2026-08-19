from __future__ import annotations

from pathlib import PurePosixPath

from app.knowledge.models import PersistentProjectKnowledge
from app.knowledge.schema import is_supported_version

from backend.app.knowledge.errors import KnowledgeValidationError
from backend.app.knowledge.validation_codes import (
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


    def validate_project_identity(
        self,
        project_id: str,
        knowledge: PersistentProjectKnowledge,
    ) -> None:

        if knowledge.metadata.project_id != project_id:
            raise ValueError(
                "Knowledge belongs to a different project"
            )
