from __future__ import annotations

from datetime import datetime

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


class ProjectKnowledgeGraphEntity(BaseModel):
    """Storage-independent graph entity available at runtime."""

    entity_id: str
    kind: str
    source_identity: str
    first_observed_at: datetime | None = None
    last_observed_at: datetime | None = None
    is_current: bool = True
    properties: dict[str, str] = Field(default_factory=dict)


class ProjectKnowledgeGraphRelationship(BaseModel):
    """Storage-independent directed graph relationship."""

    relationship_id: str
    kind: str
    source_entity_id: str
    target_entity_id: str
    first_observed_at: datetime | None = None
    last_observed_at: datetime | None = None
    is_current: bool = True
    properties: dict[str, str] = Field(default_factory=dict)


class ProjectKnowledgeGraph(BaseModel):
    """Runtime graph representation restored into the Project aggregate."""

    graph_id: str
    project_id: str
    entities: list[ProjectKnowledgeGraphEntity] = Field(default_factory=list)
    relationships: list[ProjectKnowledgeGraphRelationship] = Field(
        default_factory=list
    )


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

    graph: ProjectKnowledgeGraph | None = None
