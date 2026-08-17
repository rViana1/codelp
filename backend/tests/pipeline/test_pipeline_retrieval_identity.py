from pathlib import Path

from core.project import Project, ProjectMetadata

from app.retrieval.models import (
    RetrievalCollection,
    RetrievalResult,
    RetrievalQuery,
)

from app.knowledge.retrieval_mapper import (
    RetrievalKnowledgeMapper,
)


def test_retrieval_identity_is_deterministic():

    retrieval = RetrievalCollection(
        query=RetrievalQuery(
            text="how does hello work?"
        ),
        results=[
            RetrievalResult(
                chunk_id="chunk-001",
                score=0.95,
            )
        ],
    )

    first = (
        RetrievalKnowledgeMapper.from_retrieval(
            retrieval
        )
    )

    second = (
        RetrievalKnowledgeMapper.from_retrieval(
            retrieval
        )
    )

    assert len(first) == 1
    assert len(second) == 1

    assert (
        first[0].chunk_id
        ==
        second[0].chunk_id
    )

    assert (
        first[0].query_hash
        ==
        second[0].query_hash
    )

    assert (
        first[0].score
        ==
        second[0].score
    )