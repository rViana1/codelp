from datetime import datetime, timezone
from enum import Enum

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


class KnowledgeGraphEntityKind(str, Enum):
    """Persistent entity kinds represented by the project graph."""

    PROJECT = "project"
    FILE = "file"
    FILE_LOCATION = "file_location"
    FILE_CONTENT_STATE = "file_content_state"
    SYMBOL = "symbol"
    CHUNK = "chunk"
    EMBEDDING = "embedding"
    RETRIEVAL = "retrieval"
    MODULE = "module"


class KnowledgeGraphRelationshipKind(str, Enum):
    """Foundational relationships derived from persistent knowledge."""

    PROJECT_CONTAINS_FILE = "project_contains_file"
    FILE_HAS_LOCATION = "file_has_location"
    FILE_HAS_CONTENT_STATE = "file_has_content_state"
    FILE_DECLARES_SYMBOL = "file_declares_symbol"
    SYMBOL_HAS_CHUNK = "symbol_has_chunk"
    CHUNK_HAS_EMBEDDING = "chunk_has_embedding"
    CHUNK_HAS_RETRIEVAL = "chunk_has_retrieval"
    FILE_IMPORTS_MODULE = "file_imports_module"
    FILE_DEPENDS_ON_FILE = "file_depends_on_file"
    FILE_DUPLICATES_FILE = "file_duplicates_file"
    SYMBOL_DUPLICATES_SYMBOL = "symbol_duplicates_symbol"
    CHUNK_DUPLICATES_CHUNK = "chunk_duplicates_chunk"
    CHUNK_SIMILAR_TO_CHUNK = "chunk_similar_to_chunk"
    LOCATION_MOVED_TO = "location_moved_to"
    LOCATION_RENAMED_TO = "location_renamed_to"
    LOCATION_MOVED_AND_RENAMED_TO = "location_moved_and_renamed_to"
    CONTENT_STATE_EVOLVED_TO = "content_state_evolved_to"


class PersistentKnowledgeGraphEntity(PersistentKnowledgeModel):
    """One stable graph projection of a persistent project entity."""

    entity_id: str
    kind: KnowledgeGraphEntityKind
    source_identity: str
    first_observed_at: datetime | None = None
    last_observed_at: datetime | None = None
    is_current: bool = True
    properties: dict[str, str] = Field(default_factory=dict)


class PersistentKnowledgeGraphRelationship(PersistentKnowledgeModel):
    """A stable, directed relationship between two graph entities."""

    relationship_id: str
    kind: KnowledgeGraphRelationshipKind
    source_entity_id: str
    target_entity_id: str
    first_observed_at: datetime | None = None
    last_observed_at: datetime | None = None
    is_current: bool = True
    properties: dict[str, str] = Field(default_factory=dict)


class PersistentKnowledgeGraph(PersistentKnowledgeModel):
    """Storage-independent persistent graph projection for one project."""

    graph_id: str
    project_id: str
    entities: list[PersistentKnowledgeGraphEntity] = Field(
        default_factory=list
    )
    relationships: list[PersistentKnowledgeGraphRelationship] = Field(
        default_factory=list
    )


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

    structural_fingerprint: tuple[str, ...] = ()


class PersistentImportReference(PersistentKnowledgeModel):
    """Stable import observation associated with a persistent file."""

    import_id: str
    source_file_id: str
    imported_module: str
    target_file_id: str | None = None


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

    imports: list[PersistentImportReference] = Field(
        default_factory=list
    )

    graph: PersistentKnowledgeGraph | None = None
