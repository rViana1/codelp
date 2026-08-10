from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.chunking.models import CodeChunk

from .models import Embedding, EmbeddingCollection, EmbeddingProviderInfo


@runtime_checkable
class EmbeddingProvider(Protocol):
    """
    Contract implemented by embedding providers.
    """

    @property
    def info(self) -> EmbeddingProviderInfo:
        """
        Returns metadata about the provider.
        """

    def generate_embedding(
        self,
        chunk: CodeChunk,
    ) -> Embedding:
        """
        Generates an embedding for a single chunk.
        """

    def generate_embeddings(
        self,
        chunks: list[CodeChunk],
    ) -> EmbeddingCollection:
        """
        Generates embeddings for multiple chunks.
        """