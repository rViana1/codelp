from __future__ import annotations

from app.knowledge.constants import CURRENT_KNOWLEDGE_VERSION
from app.knowledge.models import PersistentProjectKnowledge
from backend.app.knowledge.errors import KnowledgeValidationError
from backend.app.knowledge.validation_codes import KNOWLEDGE_UNSUPPORTED_VERSION


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

        if (
            knowledge.metadata.version
            != CURRENT_KNOWLEDGE_VERSION
        ):
            raise KnowledgeValidationError(
                KNOWLEDGE_UNSUPPORTED_VERSION,
                "Unsupported knowledge version",
            )
            
        if not knowledge.metadata.project_id:
            raise ValueError(
                "Knowledge requires project_id"
            )

        file_ids = [
            file.file_id
            for file in knowledge.files
        ]

        if len(file_ids) != len(set(file_ids)):
            raise ValueError(
                "Duplicate file identities detected"
            )

        file_id_set = set(file_ids)

        symbol_ids = [
            symbol.symbol_id
            for symbol in knowledge.symbols
        ]

        if len(symbol_ids) != len(set(symbol_ids)):
            raise ValueError(
                "Duplicate symbol identities detected"
            )

        for symbol in knowledge.symbols:
            if symbol.file_id not in file_id_set:
                raise ValueError(
                    "Symbol references unknown file identity"
                )

        symbol_id_set = set(symbol_ids)

        chunk_ids = [
            chunk.chunk_id
            for chunk in knowledge.chunks
        ]

        if len(chunk_ids) != len(set(chunk_ids)):
            raise ValueError(
                "Duplicate chunk identities detected"
            )

        for chunk in knowledge.chunks:
            if chunk.symbol_id not in symbol_id_set:
                raise ValueError(
                    "Chunk references unknown symbol identity"
                )
                
        chunk_id_set = set(chunk_ids)

        for embedding in knowledge.embeddings:
            if embedding.chunk_id not in chunk_id_set:
                raise ValueError(
                    "Embedding references unknown chunk identity"
                )
                
        for retrieval in knowledge.retrieval:
            if retrieval.chunk_id not in chunk_id_set:
                raise ValueError(
                    "Retrieval references unknown chunk identity"
                )
        for file in knowledge.files:

            if not file.file_id:
                raise ValueError(
                    "File requires identity"
                )

            if not file.path:
                raise ValueError(
                    "File requires path"
                )


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
                
        for file in knowledge.files:

            if not file.content_hash:
                raise ValueError(
                    "File requires content hash"
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
        """
        Validates that persisted knowledge belongs to the project.
        """

        if (
            knowledge.metadata.project_id
            != project_id
        ):
            raise ValueError(
                "Knowledge belongs to a different project"
            )