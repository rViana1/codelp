"""
Application service responsible for project retrieval operations.

Retrieval reads project knowledge and does not modify the Project aggregate.
"""

from __future__ import annotations

from core.project import Project

from app.embeddings.models import EmbeddingCollection

from .models import (
    RetrievalCollection,
    RetrievalQuery,
)
from .retriever import Retriever


class RetrievalService:
    """
    Application service orchestrating retrieval from project knowledge.

    The service connects the Project aggregate with the Retriever engine.

    Responsibilities
    --------------
    - access project embedding knowledge;
    - delegate similarity search;
    - return retrieval results.

    The Project is not modified.
    """

    def __init__(
        self,
        retriever: Retriever,
    ) -> None:

        self.retriever = retriever

    def retrieve_project(
        self,
        project: Project,
        query: RetrievalQuery,
        query_vector: list[float],
    ) -> RetrievalCollection:
        """
        Retrieves relevant chunks from project embeddings.

        Parameters
        ----------
        project:
            Project aggregate containing embedding knowledge.

        query:
            Retrieval request.

        query_vector:
            Vector representation of the query.

        Returns
        -------
        RetrievalCollection
            Ranked retrieval results.
        """

        if project.embedding_result is None:
            project.diagnostics.append(
                "Project has no embedding_result"
            )

            return RetrievalCollection(
                query=query,
                results=[],
            )

        embeddings: EmbeddingCollection = (
            project.embedding_result
        )

        from app.embeddings.store import InMemoryVectorStore

        store = InMemoryVectorStore()

        store.add_many(
            embeddings.embeddings
        )

        return self.retriever.retrieve(
            query,
            query_vector,
            store,
        )
