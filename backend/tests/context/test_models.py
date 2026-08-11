from app.context.models import (
    ContextChunk,
    PromptContext,
)


def test_context_chunk_creation() -> None:

    chunk = ContextChunk(
        chunk_id="chunk_auth",
        content="def authenticate(): pass",
        score=0.95,
    )

    assert chunk.chunk_id == "chunk_auth"

    assert chunk.content == (
        "def authenticate(): pass"
    )

    assert chunk.score == 0.95


def test_prompt_context_defaults() -> None:

    context = PromptContext(
        query="authentication",
        context_id="ctx_001",
    )

    assert context.query == "authentication"

    assert context.context_id == "ctx_001"

    assert context.chunks == []

    assert context.max_tokens == 4000

    assert context.total_tokens == 0

    assert context.source_chunks_count == 0


def test_prompt_context_preserves_order() -> None:

    context = PromptContext(
        query="authentication",
        context_id="ctx_001",
        chunks=[
            ContextChunk(
                chunk_id="chunk_auth",
                content="auth",
                score=1.0,
            ),
            ContextChunk(
                chunk_id="chunk_user",
                content="user",
                score=0.8,
            ),
        ],
    )

    assert [
        chunk.chunk_id
        for chunk in context.chunks
    ] == [
        "chunk_auth",
        "chunk_user",
    ]

    assert context.source_chunks_count == 2