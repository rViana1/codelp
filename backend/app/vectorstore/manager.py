"""
Vector store lifecycle management.

Responsible for associating project knowledge with vector stores.
"""

from __future__ import annotations

from pathlib import Path

from app.embeddings.models import EmbeddingCollection

from app.vectorstore.interfaces import VectorStore

from app.vectorstore.factory import VectorStoreFactory

class VectorStoreManager:
    """
    Manages vector stores associated with projects.

    The manager hides the concrete vector storage
    implementation from application services.

    Current implementation:
    - In-memory vector stores.

    Future implementations may include:
    - persistent vector databases;
    - remote vector services;
    - distributed storage.
    """

    def __init__(
        self,
        factory: VectorStoreFactory | None = None,
    ) -> None:
        self._stores: dict[str, VectorStore] = {}

        self.factory = (
            factory
            if factory is not None
            else VectorStoreFactory()
        )

    def register_project(
        self,
        project_path: Path,
        embeddings: EmbeddingCollection,
    ) -> None:
        """
        Creates and registers a vector store for a project.

        Existing stores for the same project are replaced.
        """

        store = self.factory.create()

        store.add_many(
            embeddings.embeddings
        )

        self._stores[str(project_path)] = store

    def get_project_store(
        self,
        project_path: Path,
    ) -> VectorStore | None:
        """
        Returns the vector store associated with a project.
        """

        return self._stores.get(
            str(project_path)
        )

    def remove_project(
        self,
        project_path: Path,
    ) -> None:
        """
        Removes a project's vector store.
        """

        self._stores.pop(
            str(project_path),
            None,
        )

    def clear(self) -> None:
        """
        Removes all registered vector stores.
        """

        self._stores.clear()
