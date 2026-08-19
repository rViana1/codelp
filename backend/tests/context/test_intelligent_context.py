from app.chunking.models import ChunkCollection, ChunkKind, CodeChunk
from app.context.builder import ContextBuilder
from app.retrieval.models import (
    RetrievalCollection,
    RetrievalQuery,
    RetrievalResult,
)


def enriched_retrieval() -> RetrievalCollection:
    return RetrievalCollection(
        query=RetrievalQuery(text="find auth"),
        results=[
            RetrievalResult(
                chunk_id="chunk-auth",
                score=0.81,
                semantic_score=0.9,
                structural_score=0.6,
                historical_score=0.2,
                reasons=("semantic_match", "related through dependency"),
                relationship_ids=("rel-1",),
                provenance_entity_ids=("entity-1",),
            )
        ],
    )


def chunks() -> ChunkCollection:
    return ChunkCollection(
        chunks=[
            CodeChunk(
                id="chunk-auth",
                file_path="auth.py",
                kind=ChunkKind.FUNCTION,
                content="def authenticate(): pass",
                start_line=1,
                end_line=1,
            )
        ]
    )


def test_context_preserves_selection_explanation_and_provenance():
    context = ContextBuilder().build(enriched_retrieval(), chunks())
    selected = context.chunks[0]

    assert selected.selection_reasons == (
        "semantic_match",
        "related through dependency",
    )
    assert selected.relationship_ids == ("rel-1",)
    assert selected.provenance_entity_ids == ("entity-1",)
    assert selected.historical_score == 0.2


def test_context_identity_is_deterministic_for_same_evidence():
    builder = ContextBuilder()

    first = builder.build(enriched_retrieval(), chunks())
    second = builder.build(enriched_retrieval(), chunks())

    assert first.context_id == second.context_id


def test_context_identity_uses_only_selected_chunks():
    builder = ContextBuilder()
    retrieval = enriched_retrieval()
    with_unknown = retrieval.model_copy(deep=True)
    with_unknown.results.append(
        RetrievalResult(chunk_id="unknown", score=1.0)
    )

    first = builder.build(retrieval, chunks())
    second = builder.build(with_unknown, chunks())

    assert first.context_id == second.context_id


def test_context_identity_changes_when_selection_evidence_changes():
    builder = ContextBuilder()
    changed = enriched_retrieval()
    changed.results[0].reasons = ("different graph evidence",)

    first = builder.build(enriched_retrieval(), chunks())
    second = builder.build(changed, chunks())

    assert first.context_id != second.context_id
