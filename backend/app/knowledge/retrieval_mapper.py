from __future__ import annotations

import hashlib

from app.retrieval.models import (
    RetrievalCollection,
)

from app.knowledge.models import (
    PersistentRetrievalMetadata,
)


class RetrievalKnowledgeMapper:
    """
    Converts retrieval results into persistent metadata.

    Does not persist query text.
    Stores query identity through hashing.
    """

    @staticmethod
    def from_retrieval(
        retrieval: RetrievalCollection | None,
    ) -> list[PersistentRetrievalMetadata]:

        if retrieval is None:
            return []

        query_hash = (
            RetrievalKnowledgeMapper._hash_query(
                retrieval.query.text
            )
        )

        result = []

        for item in sorted(
            retrieval.results,
            key=lambda value: value.chunk_id,
        ):

            result.append(
                PersistentRetrievalMetadata(
                    chunk_id=item.chunk_id,
                    query_hash=query_hash,
                    score=item.score,
                )
            )

        return result


    @staticmethod
    def _hash_query(
        query: str,
    ) -> str:

        return hashlib.sha256(
            query.encode("utf-8")
        ).hexdigest()
