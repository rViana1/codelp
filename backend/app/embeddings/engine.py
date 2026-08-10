from __future__ import annotations

from core.project import Project

from app.chunking.models import ChunkCollection

from .models import EmbeddingCollection
from .providers import EmbeddingProvider


class EmbeddingEngine:
    """
    Orchestrates embedding generation from semantic chunks.
    """

    def __init__(
        self,
        provider: EmbeddingProvider,
    ) -> None:

        self.provider = provider

    def embed(
        self,
        chunks: ChunkCollection,
    ) -> EmbeddingCollection:
        """
        Generates embeddings for a collection of chunks.
        """

        ordered_chunks = sorted(
            chunks.chunks,
            key=lambda chunk: chunk.id,
        )

        return self.provider.generate_embeddings(
            ordered_chunks
        )

    def embed_project(
        self,
        project: Project,
    ) -> Project:
        """
        Generates embeddings for the project's chunk collection and
        updates the Project aggregate.
        """

        if project.chunk_result is None:
            raise ValueError(
                "Project has no chunk_result"
            )

        project.embedding_result = self.embed(
            project.chunk_result
        )

        return project