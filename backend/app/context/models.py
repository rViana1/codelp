from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ContextChunk(BaseModel):
    """
    Represents a chunk selected for the final context.

    A ContextChunk preserves the relationship between
    retrieval results and the source knowledge used by
    downstream consumers.
    """

    chunk_id: str

    content: str

    score: float

    semantic_score: float | None = None

    structural_score: float = 0.0

    historical_score: float = 0.0

    selection_reasons: tuple[str, ...] = ()

    relationship_ids: tuple[str, ...] = ()

    provenance_entity_ids: tuple[str, ...] = ()


class PromptContext(BaseModel):
    """
    Structured context prepared for external consumers.

    This model represents the knowledge selected from the
    project before being sent to an LLM or another consumer.
    """

    query: str

    context_id: str

    chunks: list[ContextChunk] = Field(
        default_factory=list
    )

    max_tokens: int = 4000

    total_tokens: int = 0

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def source_chunks_count(self) -> int:
        """
        Returns the number of chunks included in the context.
        """

        return len(self.chunks)
