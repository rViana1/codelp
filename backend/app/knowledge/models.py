from datetime import datetime, timezone
from pydantic import BaseModel, Field


class PersistentKnowledgeMetadata(BaseModel):
    project_id: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class PersistentSymbol(BaseModel):
    symbol_id: str
    file_path: str
    name: str
    symbol_type: str


class PersistentChunk(BaseModel):
    chunk_id: str
    symbol_id: str
    file_path: str
    content_hash: str


class PersistentEmbeddingMetadata(BaseModel):
    chunk_id: str
    provider: str
    embedding_hash: str


class PersistentRetrievalMetadata(BaseModel):
    chunk_id: str
    query_hash: str
    score: float

class PersistentFileIdentity(BaseModel):
    """
    Represents the persistent identity of an analyzed file.

    A file identity allows Codelp to detect changes between executions.
    """

    file_id: str

    path: str

    content_hash: str


class PersistentSymbolIdentity(BaseModel):
    """
    Represents the persistent identity of a parsed symbol.
    """

    symbol_id: str

    file_id: str

    name: str

    symbol_type: str


class PersistentChunkIdentity(BaseModel):
    """
    Represents the persistent identity of a semantic chunk.
    """

    chunk_id: str

    symbol_id: str

    content_hash: str

class PersistentProjectKnowledge(BaseModel):

    metadata: PersistentKnowledgeMetadata

    files: list[PersistentFileIdentity] = Field(
        default_factory=list
    )

    symbols: list[PersistentSymbolIdentity] = Field(
        default_factory=list
    )

    chunks: list[PersistentChunkIdentity] = Field(
        default_factory=list
    )

    embeddings: list[PersistentEmbeddingMetadata] = Field(
        default_factory=list
    )

    retrieval: list[PersistentRetrievalMetadata] = Field(
        default_factory=list
    )