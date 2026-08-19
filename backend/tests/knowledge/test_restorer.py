from pathlib import Path

from backend.app.knowledge.parser_mapper import ParserKnowledgeMapper
from backend.tests.core import project
from core.project import Project, ProjectMetadata, ProjectConfiguration

from app.knowledge.models import (
    PersistentChunkIdentity,
    PersistentEmbeddingMetadata,
    PersistentFileIdentity,
    PersistentFileFingerprint,
    PersistentFileLocation,
    PersistentKnowledgeMetadata,
    PersistentProjectConfiguration,
    PersistentProjectKnowledge,
    PersistentRetrievalMetadata,
    PersistentSymbolIdentity,
)

from app.chunking.models import (
    ChunkCollection,
    ChunkKind,
    CodeChunk,
)

from app.embeddings.models import (
    Embedding,
    EmbeddingCollection,
    EmbeddingProviderInfo,
)

from app.retrieval.models import (
    RetrievalCollection,
    RetrievalQuery,
    RetrievalResult,
)

from app.parser.models import (
    ParsedFile,
    ParsedProject,
    FunctionSymbol,
)

from app.knowledge.builder import KnowledgeBuilder

from app.knowledge.restorer import KnowledgeRestorer


def test_restorer_updates_project_state(tmp_path):

    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=Path(tmp_path),
        )
    )

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        )
    )

    restorer = KnowledgeRestorer()

    result = restorer.restore(
        project,
        knowledge,
    )

    assert result is project

    assert (
        "Restored knowledge for project demo"
        in project.diagnostics
    )


def test_restorer_restores_project_configuration(tmp_path):

    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=Path(tmp_path),
        ),
        configuration=ProjectConfiguration(
            follow_symlinks=False,
            ignore_hidden=True,
            max_file_size_bytes=100,
            ignored_directories={"old"},
            ignored_extensions={".old"},
        ),
    )

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        ),
        configuration=PersistentProjectConfiguration(
            follow_symlinks=True,
            ignore_hidden=False,
            max_file_size_bytes=123456,
            ignored_directories={"build", ".git"},
            ignored_extensions={".pyc", ".tmp"},
        ),
    )

    restorer = KnowledgeRestorer()

    result = restorer.restore(
        project,
        knowledge,
    )

    assert result is project

    assert project.configuration.follow_symlinks is True
    assert project.configuration.ignore_hidden is False
    assert project.configuration.max_file_size_bytes == 123456
    assert project.configuration.ignored_directories == {
        "build",
        ".git",
    }
    assert project.configuration.ignored_extensions == {
        ".pyc",
        ".tmp",
    }
    
    
def test_restorer_restores_knowledge_identities(tmp_path):

    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=Path(tmp_path),
        )
    )

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        ),
        files=[
            PersistentFileIdentity(
                file_id="file-1",
                locations=[
                    PersistentFileLocation(
                        path="src/main.py",
                        first_seen="2026-01-01T00:00:00Z",
                        last_seen="2026-01-01T00:00:00Z",
                    )
                ],
                fingerprints=[
                    PersistentFileFingerprint(
                        content_hash="hash-1",
                        size_bytes=1,
                        generated_at="2026-01-01T00:00:00Z",
                        last_seen="2026-01-01T00:00:00Z",
                    )
                ],
            )
        ],
        symbols=[
            PersistentSymbolIdentity(
                symbol_id="symbol-1",
                file_id="file-1",
                name="hello",
                symbol_type="function",
            )
        ],
        chunks=[
            PersistentChunkIdentity(
                chunk_id="chunk-1",
                symbol_id="symbol-1",
                content_hash="chunk-hash-1",
            )
        ],
    )

    restorer = KnowledgeRestorer()

    result = restorer.restore(
        project,
        knowledge,
    )

    assert result is project
    assert project.knowledge_state is not None

    assert len(project.knowledge_state.files) == 1
    assert project.knowledge_state.files[0].file_id == "file-1"
    assert project.knowledge_state.files[0].path == "src/main.py"

    assert len(project.knowledge_state.symbols) == 1
    assert project.knowledge_state.symbols[0].symbol_id == "symbol-1"
    assert project.knowledge_state.symbols[0].file_id == "file-1"

    assert len(project.knowledge_state.chunks) == 1
    assert project.knowledge_state.chunks[0].chunk_id == "chunk-1"
    assert project.knowledge_state.chunks[0].symbol_id == "symbol-1"
    
    
def test_restorer_restores_embedding_knowledge(tmp_path):
    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=Path(tmp_path),
        )
    )

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        ),
        chunks=[
            PersistentChunkIdentity(
                chunk_id="chunk-1",
                symbol_id="symbol-1",
                content_hash="chunk-hash-1",
            )
        ],
        embeddings=[
            PersistentEmbeddingMetadata(
                chunk_id="chunk-1",
                provider="fake",
                embedding_hash="embedding-hash-1",
            )
        ],
    )

    restored = KnowledgeRestorer().restore(
        project,
        knowledge,
    )

    assert restored.knowledge_state is not None

    assert len(
        restored.knowledge_state.embeddings
    ) == 1

    embedding = (
        restored.knowledge_state.embeddings[0]
    )

    assert embedding.chunk_id == "chunk-1"
    assert embedding.provider == "fake"
    assert (
        embedding.embedding_hash
        == "embedding-hash-1"
    )


def test_restorer_restores_retrieval_knowledge(tmp_path):
    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=Path(tmp_path),
        )
    )

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        ),
        chunks=[
            PersistentChunkIdentity(
                chunk_id="chunk-1",
                symbol_id="symbol-1",
                content_hash="chunk-hash-1",
            )
        ],
        retrieval=[
            PersistentRetrievalMetadata(
                chunk_id="chunk-1",
                query_hash="query-hash-1",
                score=0.95,
            )
        ],
    )

    restored = KnowledgeRestorer().restore(
        project,
        knowledge,
    )

    assert restored.knowledge_state is not None

    assert len(
        restored.knowledge_state.retrieval
    ) == 1

    retrieval = (
        restored.knowledge_state.retrieval[0]
    )

    assert retrieval.chunk_id == "chunk-1"
    assert retrieval.query_hash == "query-hash-1"
    assert retrieval.score == 0.95
    
    
def test_restore_roundtrip_preserves_all_identity_relationships(tmp_path):
    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=Path(tmp_path),
        )
    )

    project.statistics.scanned_files = [
        Path(tmp_path) / "main.py"
    ]

    project.parser_result = ParsedProject(
        files=[
            ParsedFile(
                path=Path(tmp_path) / "main.py",
                language="python",
                functions=[
                    FunctionSymbol(
                        name="hello",
                        start_line=1,
                        end_line=2,
                    )
                ],
            )
        ]
    )

    project.chunk_result = ChunkCollection(
        chunks=[
            CodeChunk(
                id="chunk-1",
                file_path=str(
                    Path(tmp_path) / "main.py"
                ),
                symbol_id=(
                    ParserKnowledgeMapper
                    ._create_symbol_id(
                        str(
                            Path(tmp_path) / "main.py"
                        ),
                        "hello",
                        "function",
                    )
                ),
                kind=ChunkKind.FUNCTION,
                content="def hello(): return 42",
                start_line=1,
                end_line=2,
            )
        ]
    )

    project.embedding_result = EmbeddingCollection(
        provider=EmbeddingProviderInfo(
            name="fake",
            model="fake-model",
            dimensions=5,
        ),
        embeddings=[
            Embedding(
                chunk_id="chunk-1",
                vector=[
                    0.1,
                    0.2,
                    0.3,
                    0.4,
                    0.5,
                ],
            )
        ],
    )

    project.retrieval_result = RetrievalCollection(
        query=RetrievalQuery(
            text="hello function"
        ),
        results=[
            RetrievalResult(
                chunk_id="chunk-1",
                score=0.9,
            )
        ],
    )

    knowledge = KnowledgeBuilder().build(
        project
    )

    symbol_id = (
        knowledge.symbols[0].symbol_id
    )

    knowledge.chunks[0].symbol_id = symbol_id

    restored_project = KnowledgeRestorer().restore(
        Project(
            metadata=project.metadata
        ),
        knowledge,
    )

    assert restored_project.knowledge_state is not None

    state = restored_project.knowledge_state

    assert len(state.files) == 1
    assert len(state.symbols) == 1
    assert len(state.chunks) == 1
    assert len(state.embeddings) == 1
    assert len(state.retrieval) == 1

    assert (
        state.symbols[0].file_id
        ==
        state.files[0].file_id
    )

    assert (
        state.chunks[0].symbol_id
        ==
        state.symbols[0].symbol_id
    )

    assert (
        state.embeddings[0].chunk_id
        ==
        state.chunks[0].chunk_id
    )

    assert (
        state.retrieval[0].chunk_id
        ==
        state.chunks[0].chunk_id
    )
