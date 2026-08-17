from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.knowledge.constants import CURRENT_KNOWLEDGE_VERSION


class PersistentKnowledgeMetadata(BaseModel):
    project_id: str

    version: str = CURRENT_KNOWLEDGE_VERSION

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class PersistentProjectConfiguration(BaseModel):
    """
    Represents the persisted configuration of a project.

    Only stable configuration values are persisted.
    Runtime analysis state is intentionally excluded.
    """

    follow_symlinks: bool = False

    ignore_hidden: bool = True

    max_file_size_bytes: int = 5 * 1024 * 1024

    ignored_directories: set[str] = Field(
        default_factory=set
    )

    ignored_extensions: set[str] = Field(
        default_factory=set
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

    configuration: PersistentProjectConfiguration = Field(
        default_factory=PersistentProjectConfiguration
    )

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