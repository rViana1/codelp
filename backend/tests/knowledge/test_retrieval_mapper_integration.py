from pathlib import Path

from core.project import Project
from core.project.models import ProjectMetadata

from app.retrieval.models import (
    RetrievalCollection,
    RetrievalQuery,
    RetrievalResult,
)

from app.knowledge.builder import KnowledgeBuilder


def test_builder_persists_retrieval_metadata():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        )
    )

    project.retrieval_result = RetrievalCollection(
        query=RetrievalQuery(
            text="find authentication code",
        ),
        results=[
            RetrievalResult(
                chunk_id="chunk-1",
                score=0.95,
            )
        ],
    )

    knowledge = KnowledgeBuilder().build(
        project
    )

    assert len(
        knowledge.retrieval
    ) == 1

    assert (
        knowledge.retrieval[0].chunk_id
        == "chunk-1"
    )

    assert (
        knowledge.retrieval[0].score
        == 0.95
    )

    assert (
        knowledge.retrieval[0].query_hash
        != ""
    )
