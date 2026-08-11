from __future__ import annotations

from typing import Protocol

from .models import Embedding


class VectorStore(Protocol):
    """
    Interface for vector storage implementations.

    Retrieval depends only on this contract,
    not on a concrete storage implementation.
    """

    def all(self) -> list[Embedding]:
        """
        Return all stored embeddings.
        """
        ...
