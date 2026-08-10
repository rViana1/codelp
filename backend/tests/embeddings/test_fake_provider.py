from app.chunking.models import CodeChunk, ChunkKind
from app.embeddings.fake_provider import FakeEmbeddingProvider


def make_chunk(content: str) -> CodeChunk:

    return CodeChunk(
        id=f"chunk::{hash(content)}",
        kind=ChunkKind.FUNCTION,
        file_path="src/main.py",
        symbol="hello",
        content=content,
        start_line=1,
        end_line=2,
    )


def test_generate_single_embedding() -> None:

    provider = FakeEmbeddingProvider(dimensions=4)

    embedding = provider.generate_embedding(
        make_chunk("def hello(): pass")
    )

    assert embedding.chunk_id.startswith("chunk::")

    assert len(embedding.vector) == 4


def test_same_content_generates_same_vector() -> None:

    provider = FakeEmbeddingProvider(dimensions=8)

    first = provider.generate_embedding(
        make_chunk("same")
    )

    second = provider.generate_embedding(
        make_chunk("same")
    )

    assert first.vector == second.vector


def test_different_content_generates_different_vector() -> None:

    provider = FakeEmbeddingProvider(dimensions=8)

    first = provider.generate_embedding(
        make_chunk("a")
    )

    second = provider.generate_embedding(
        make_chunk("b")
    )

    assert first.vector != second.vector


def test_generate_multiple_embeddings() -> None:

    provider = FakeEmbeddingProvider(dimensions=3)

    result = provider.generate_embeddings(
        [
            make_chunk("a"),
            make_chunk("b"),
        ]
    )

    assert result.provider.name == "fake"

    assert result.provider.dimensions == 3

    assert len(result.embeddings) == 2
