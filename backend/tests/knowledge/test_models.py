from app.knowledge.models import (
    PersistentKnowledgeMetadata,
    PersistentSymbolIdentity,
    PersistentChunkIdentity,
    PersistentEmbeddingMetadata,
    PersistentRetrievalMetadata,
    PersistentProjectKnowledge,
    PersistentFileIdentity,
)


def test_metadata_creation():
    metadata = PersistentKnowledgeMetadata(
        project_id="test-project"
    )

    assert metadata.project_id == "test-project"
    assert metadata.created_at is not None
    assert metadata.updated_at is not None


def test_symbol_identity_preservation():
    symbol = PersistentSymbolIdentity(
        symbol_id="src/main.py::hello",
        file_id="src/main.py",
        name="hello",
        symbol_type="function",
    )

    assert symbol.symbol_id == "src/main.py::hello"


def test_chunk_identity_preservation():
    chunk = PersistentChunkIdentity(
        chunk_id="chunk-001",
        symbol_id="src/main.py::hello",
        content_hash="hash123",
    )

    assert chunk.chunk_id == "chunk-001"


def test_embedding_metadata_preservation():
    embedding = PersistentEmbeddingMetadata(
        chunk_id="chunk-001",
        provider="fake",
        embedding_hash="embedding123",
    )

    assert embedding.chunk_id == "chunk-001"


def test_retrieval_metadata_preservation():
    retrieval = PersistentRetrievalMetadata(
        chunk_id="chunk-001",
        query_hash="query123",
        score=0.95,
    )

    assert retrieval.score == 0.95


def test_project_knowledge_serialization():
    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="test-project"
        ),
        files=[
            PersistentFileIdentity(
                file_id="src/main.py",
                path="src/main.py",
                content_hash="hash123",
            )
        ],
        symbols=[
            PersistentSymbolIdentity(
                symbol_id="src/main.py::hello",
                file_id="src/main.py",
                name="hello",
                symbol_type="function",
            )
        ],
        chunks=[
            PersistentChunkIdentity(
                chunk_id="chunk-001",
                symbol_id="src/main.py::hello",
                content_hash="hash123",
            )
        ],
    )

    data = knowledge.model_dump()

    restored = PersistentProjectKnowledge(**data)

    assert restored.metadata.project_id == "test-project"
    assert restored.files[0].file_id == "src/main.py"
    assert restored.symbols[0].symbol_id == "src/main.py::hello"
    assert restored.chunks[0].chunk_id == "chunk-001"

def test_file_identity_preservation():
    file = PersistentFileIdentity(
        file_id="src/main.py",
        path="src/main.py",
        content_hash="hash123",
    )

    assert file.file_id == "src/main.py"
    assert file.path == "src/main.py"
    assert file.content_hash == "hash123"