"""
Domain models for retrieval operations.

Retrieval models represent query requests and search results
generated from the project knowledge base.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class RetrievalQuery(BaseModel):
    """
    Represents a semantic retrieval request.
    """

    text: str

    limit: int = 5


class RetrievalResult(BaseModel):
    """
    Represents a single retrieved knowledge item.
    """

    chunk_id: str

    score: float

    semantic_score: float | None = None

    structural_score: float = 0.0

    historical_score: float = 0.0

    reasons: tuple[str, ...] = ()

    relationship_ids: tuple[str, ...] = ()

    provenance_entity_ids: tuple[str, ...] = ()


class RetrievalCollection(BaseModel):
    """
    Represents an ordered collection of retrieval results.
    """

    query: RetrievalQuery

    results: list[RetrievalResult] = Field(default_factory=list)
