from __future__ import annotations

from typing import Protocol

from app.embeddings.models import Embedding


class VectorStore(Protocol):
    """
    Abstraction for vector storage.

    Retrieval depends only on this contract,
    not on a concrete storage implementation.
    """

    def all(self) -> list[Embedding]:
        """
        Return all stored embeddings.
        """
        ...
