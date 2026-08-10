from app.chunking.models import (
    ChunkCollection,
    ChunkKind,
    CodeChunk,
)
from app.embeddings.engine import EmbeddingEngine
from app.embeddings.fake_provider import FakeEmbeddingProvider


def make_chunk(chunk_id: str, content: str) -> CodeChunk:

    return CodeChunk(
        id=chunk_id,
        kind=ChunkKind.FUNCTION,
        file_path="src/main.py",
        symbol="hello",
        content=content,
        start_line=1,
        end_line=2,
    )


def test_embed_empty_collection() -> None:

    engine = EmbeddingEngine(
        FakeEmbeddingProvider()
    )

    result = engine.embed(
        ChunkCollection()
    )

    assert result.embeddings == []


def test_embed_single_chunk() -> None:

    engine = EmbeddingEngine(
        FakeEmbeddingProvider(dimensions=4)
    )

    result = engine.embed(
        ChunkCollection(
            chunks=[
                make_chunk(
                    "a",
                    "def hello(): pass",
                )
            ]
        )
    )

    assert len(result.embeddings) == 1

    assert result.embeddings[0].chunk_id == "a"

    assert len(result.embeddings[0].vector) == 4


def test_embed_multiple_chunks_deterministic_order() -> None:

    engine = EmbeddingEngine(
        FakeEmbeddingProvider(dimensions=2)
    )

    result = engine.embed(
        ChunkCollection(
            chunks=[
                make_chunk("b", "b"),
                make_chunk("a", "a"),
                make_chunk("c", "c"),
            ]
        )
    )

    assert [
        embedding.chunk_id
        for embedding in result.embeddings
    ] == ["a", "b", "c"]
