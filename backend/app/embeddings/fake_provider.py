from __future__ import annotations

import hashlib

from app.chunking.models import CodeChunk

from .models import Embedding, EmbeddingCollection, EmbeddingProviderInfo
from .providers import EmbeddingProvider


class FakeEmbeddingProvider(EmbeddingProvider):
    """
    Deterministic embedding provider used for tests and development.
    """

    def __init__(
        self,
        dimensions: int = 8,
    ) -> None:

        self._dimensions = dimensions

    @property
    def info(self) -> EmbeddingProviderInfo:

        return EmbeddingProviderInfo(
            name="fake",
            model=f"fake-{self._dimensions}",
            dimensions=self._dimensions,
        )

    def generate_embedding(
        self,
        chunk: CodeChunk,
    ) -> Embedding:

        digest = hashlib.sha256(
            chunk.content.encode("utf-8")
        ).digest()

        vector = [
            digest[i] / 255.0
            for i in range(self._dimensions)
        ]

        return Embedding(
            chunk_id=chunk.id,
            vector=vector,
        )

    def generate_embeddings(
        self,
        chunks: list[CodeChunk],
    ) -> EmbeddingCollection:

        embeddings = [
            self.generate_embedding(chunk)
            for chunk in chunks
        ]

        return EmbeddingCollection(
            provider=self.info,
            embeddings=embeddings,
        )
