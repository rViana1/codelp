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

from app.vectorstore.manager import VectorStoreManager

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
        store_manager: VectorStoreManager,
    ) -> None:

        self.retriever = retriever
        self.store_manager = store_manager

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

        project_path = project.metadata.root_path

        self.store_manager.register_project(
            project_path,
            embeddings,
        )

        store = self.store_manager.get_project_store(
            project_path
        )

        if store is None:
            return RetrievalCollection(
                query=query,
                results=[],
            )

        return self.retriever.retrieve(
            query,
            query_vector,
            store,
        )
