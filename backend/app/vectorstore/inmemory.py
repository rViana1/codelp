from __future__ import annotations

from app.embeddings.models import Embedding


class InMemoryVectorStore:
    """
    Simple in-memory storage for embeddings.
    """

    def __init__(self) -> None:
        self._embeddings: dict[str, Embedding] = {}

    def add(
        self,
        embedding: Embedding,
    ) -> None:
        self._embeddings[embedding.chunk_id] = embedding

    def add_many(
        self,
        embeddings: list[Embedding],
    ) -> None:
        for embedding in embeddings:
            self.add(embedding)

    def get(
        self,
        chunk_id: str,
    ) -> Embedding | None:
        return self._embeddings.get(chunk_id)

    def contains(
        self,
        chunk_id: str,
    ) -> bool:
        return chunk_id in self._embeddings

    def all(self) -> list[Embedding]:
        return list(self._embeddings.values())
