from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


"""
Chunking domain models.

These models represent semantic chunks extracted from parsed and
indexed project knowledge.

Chunks are deterministic and identified by stable IDs derived from
symbol IDs.
"""


class ChunkKind(str, Enum):
    """
    Supported chunk kinds.
    """

    FUNCTION = "function"

    METHOD = "method"

    CLASS = "class"


class CodeChunk(BaseModel):
    """
    Represents a semantic code chunk.
    """

    id: str

    file_path: str

    symbol_id: str | None = None

    kind: ChunkKind

    content: str

    start_line: int

    end_line: int


class ChunkCollection(BaseModel):
    """
    Collection of semantic chunks.
    """

    chunks: list[CodeChunk] = Field(default_factory=list)

    diagnostics: list[str] = Field(default_factory=list)
