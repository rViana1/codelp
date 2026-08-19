from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field

from app.knowledge.constants import CURRENT_KNOWLEDGE_VERSION


class PersistentKnowledgeModel(BaseModel):
    """Base model for versioned knowledge snapshots.

    Persisted knowledge is an explicit schema.  Silently ignoring an
    unknown field can turn an old or corrupted snapshot into apparently
    valid, but incomplete, knowledge.
    """

    model_config = ConfigDict(extra="forbid")


class PersistentKnowledgeMetadata(PersistentKnowledgeModel):
    project_id: str

    version: str = CURRENT_KNOWLEDGE_VERSION

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class PersistentProjectConfiguration(PersistentKnowledgeModel):
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

class PersistentFileLocation(PersistentKnowledgeModel):
    """
    Represents a historical filesystem location of a file entity.

    A location is not the identity of the file.
    It is only a representation of where the entity existed.
    """

    path: str

    first_seen: datetime

    last_seen: datetime

    is_current: bool = True


class PersistentFileFingerprint(PersistentKnowledgeModel):
    """
    Represents a historical content state of a file entity.

    Content changes do not create a new identity.
    They create a new fingerprint state.
    """

    content_hash: str

    size_bytes: int

    generated_at: datetime

    last_seen: datetime

    is_current: bool = True


class PersistentSymbol(PersistentKnowledgeModel):
    symbol_id: str
    file_path: str
    name: str
    symbol_type: str


class PersistentChunk(PersistentKnowledgeModel):
    chunk_id: str
    symbol_id: str
    file_path: str
    content_hash: str


class PersistentEmbeddingMetadata(PersistentKnowledgeModel):
    chunk_id: str
    provider: str
    embedding_hash: str


class PersistentRetrievalMetadata(PersistentKnowledgeModel):
    chunk_id: str
    query_hash: str
    score: float


class PersistentFileIdentity(PersistentKnowledgeModel):
    """
    Represents the stable identity of an analyzed file.

    File identity is independent from filesystem location.
    Locations and content states are tracked historically.
    """

    file_id: str

    locations: list[PersistentFileLocation] = Field(
        default_factory=list
    )

    fingerprints: list[PersistentFileFingerprint] = Field(
        default_factory=list
    )


class PersistentSymbolIdentity(PersistentKnowledgeModel):
    """
    Represents the persistent identity of a parsed symbol.
    """

    symbol_id: str

    file_id: str

    name: str

    symbol_type: str


class PersistentChunkIdentity(PersistentKnowledgeModel):
    """
    Represents the persistent identity of a semantic chunk.
    """

    chunk_id: str

    symbol_id: str

    content_hash: str


class PersistentProjectKnowledge(PersistentKnowledgeModel):

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
