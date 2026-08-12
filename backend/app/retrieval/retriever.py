"""
Retrieval engine responsible for searching embeddings.
"""

from __future__ import annotations

from app.retrieval.models import (
    RetrievalCollection,
    RetrievalQuery,
    RetrievalResult,
)
from app.retrieval.similarity import cosine_similarity
from app.vectorstore.interfaces import VectorStore

class Retriever:
    """
    Retrieves relevant embeddings based on vector similarity.

    The retriever does not generate query embeddings.
    It receives an already encoded query vector and is only
    responsible for similarity calculation, ranking and result limiting.
    """

    def retrieve(
        self,
        query: RetrievalQuery,
        query_vector: list[float],
        store: VectorStore,
    ) -> RetrievalCollection:
        """
        Retrieve embeddings ranked by similarity.

        Parameters
        ----------
        query:
            Original retrieval request.

        query_vector:
            Vector representation of the query.
            Query encoding is handled outside the Retriever.

        store:
            Vector storage abstraction containing embeddings.
        """

        results: list[RetrievalResult] = []

        for embedding in store.all():
            score = cosine_similarity(
                query_vector,
                embedding.vector,
            )

            results.append(
                RetrievalResult(
                    chunk_id=embedding.chunk_id,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: (
                -result.score,
                result.chunk_id,
            )
        )

        return RetrievalCollection(
            query=query,
            results=results[: query.limit],
        )