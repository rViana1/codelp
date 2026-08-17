from __future__ import annotations

from pydantic import BaseModel, Field


class ProjectFileKnowledge(BaseModel):
    """
    Represents the persistent identity of a project file
    available to the domain.
    """

    file_id: str

    path: str

    content_hash: str


class ProjectSymbolKnowledge(BaseModel):
    """
    Represents the persistent identity of a project symbol
    available to the domain.
    """

    symbol_id: str

    file_id: str

    name: str

    symbol_type: str


class ProjectChunkKnowledge(BaseModel):
    """
    Represents the persistent identity of a project chunk
    available to the domain.
    """

    chunk_id: str

    symbol_id: str

    content_hash: str


class ProjectEmbeddingKnowledge(BaseModel):
    """
    Represents persisted embedding knowledge associated with
    a semantic chunk.

    The embedding vector itself is intentionally excluded from
    the domain knowledge state.
    """

    chunk_id: str

    provider: str

    embedding_hash: str


class ProjectRetrievalKnowledge(BaseModel):
    """
    Represents persisted retrieval knowledge associated with
    a semantic chunk.

    The original query text is intentionally excluded.
    """

    chunk_id: str

    query_hash: str

    score: float


class ProjectKnowledgeState(BaseModel):
    """
    Represents the knowledge state restored into a Project.

    This is a domain representation and must remain independent
    from persistence implementations.
    """

    files: list[ProjectFileKnowledge] = Field(
        default_factory=list
    )

    symbols: list[ProjectSymbolKnowledge] = Field(
        default_factory=list
    )

    chunks: list[ProjectChunkKnowledge] = Field(
        default_factory=list
    )

    embeddings: list[ProjectEmbeddingKnowledge] = Field(
        default_factory=list
    )

    retrieval: list[ProjectRetrievalKnowledge] = Field(
        default_factory=list
    )