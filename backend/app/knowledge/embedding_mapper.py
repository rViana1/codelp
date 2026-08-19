from __future__ import annotations

import hashlib

from app.embeddings.models import (
    EmbeddingCollection,
)

from app.knowledge.models import (
    PersistentEmbeddingMetadata,
)


class EmbeddingKnowledgeMapper:
    """
    Converts embedding results into persistent metadata.

    Stores identity information only.
    Does not persist vectors.
    """

    @staticmethod
    def from_embeddings(
        embeddings: EmbeddingCollection | None,
        chunk_identity_by_source: dict[str, str] | None = None,
    ) -> list[PersistentEmbeddingMetadata]:

        if embeddings is None:
            return []

        chunk_identity_by_source = (
            chunk_identity_by_source or {}
        )

        provider = (
            embeddings.provider.name
        )

        result = []

        for embedding in sorted(
            embeddings.embeddings,
            key=lambda item: item.chunk_id,
        ):

            result.append(
                PersistentEmbeddingMetadata(
                    chunk_id=chunk_identity_by_source.get(
                        embedding.chunk_id,
                        embedding.chunk_id,
                    ),
                    provider=provider,
                    embedding_hash=EmbeddingKnowledgeMapper._hash_vector(
                        embedding.vector
                    ),
                )
            )

        return result


    @staticmethod
    def _hash_vector(
        vector: list[float],
    ) -> str:

        value = ",".join(
            str(item)
            for item in vector
        )

        return hashlib.sha256(
            value.encode("utf-8")
        ).hexdigest()
