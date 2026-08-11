from __future__ import annotations

from pydantic import BaseModel, Field


class EmbeddingProviderInfo(BaseModel):
    """
    Metadata describing the provider that generated the embeddings.
    """

    name: str
    model: str
    dimensions: int


class Embedding(BaseModel):
    """
    Vector representation associated with a semantic chunk.
    """

    chunk_id: str
    vector: list[float]


class EmbeddingCollection(BaseModel):
    """
    Collection of embeddings generated for a project.
    """

    provider: EmbeddingProviderInfo
    embeddings: list[Embedding] = Field(default_factory=list)
    
    def all(self) -> list[Embedding]:
        """
        Returns all stored embeddings.

        This abstraction allows retrieval systems to consume
        embeddings without depending on the storage implementation.
        """

        return self.embeddings
