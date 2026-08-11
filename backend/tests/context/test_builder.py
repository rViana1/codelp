from app.chunking.models import (
    ChunkCollection,
    CodeChunk,
    ChunkKind,
)

from app.context.builder import ContextBuilder

from app.retrieval.models import (
    RetrievalCollection,
    RetrievalQuery,
    RetrievalResult,
)


def create_chunks() -> ChunkCollection:
    return ChunkCollection(
        chunks=[
            CodeChunk(
                id="chunk_auth",
                file_path="auth.py",
                kind=ChunkKind.FUNCTION,
                content="def authenticate(): pass",
                start_line=1,
                end_line=1,
            ),
            CodeChunk(
                id="chunk_database",
                file_path="database.py",
                kind=ChunkKind.FUNCTION,
                content="def connect(): pass",
                start_line=1,
                end_line=1,
            ),
        ]
    )


def create_retrieval() -> RetrievalCollection:
    return RetrievalCollection(
        query=RetrievalQuery(
            text="authentication",
        ),
        results=[
            RetrievalResult(
                chunk_id="chunk_auth",
                score=0.95,
            ),
            RetrievalResult(
                chunk_id="chunk_database",
                score=0.50,
            ),
        ],
    )


def test_builder_creates_context_from_retrieval():

    builder = ContextBuilder()

    context = builder.build(
        create_retrieval(),
        create_chunks(),
    )

    assert context.query == "authentication"

    assert [
        chunk.chunk_id
        for chunk in context.chunks
    ] == [
        "chunk_auth",
        "chunk_database",
    ]


def test_builder_preserves_retrieval_order():

    builder = ContextBuilder()

    retrieval = RetrievalCollection(
        query=RetrievalQuery(
            text="test",
        ),
        results=[
            RetrievalResult(
                chunk_id="chunk_database",
                score=0.50,
            ),
            RetrievalResult(
                chunk_id="chunk_auth",
                score=0.95,
            ),
        ],
    )

    context = builder.build(
        retrieval,
        create_chunks(),
    )

    assert [
        chunk.chunk_id
        for chunk in context.chunks
    ] == [
        "chunk_database",
        "chunk_auth",
    ]


def test_builder_ignores_unknown_chunks():

    builder = ContextBuilder()

    retrieval = RetrievalCollection(
        query=RetrievalQuery(
            text="missing",
        ),
        results=[
            RetrievalResult(
                chunk_id="unknown",
                score=1.0,
            )
        ],
    )

    context = builder.build(
        retrieval,
        create_chunks(),
    )

    assert context.chunks == []
