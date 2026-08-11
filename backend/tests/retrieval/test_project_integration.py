from pathlib import Path

from core.project import Project, ProjectMetadata

from app.embeddings.models import (
    Embedding,
    EmbeddingCollection,
    EmbeddingProviderInfo,
)
from app.retrieval.models import RetrievalQuery
from app.retrieval.retriever import Retriever
from app.retrieval.service import RetrievalService


def create_project() -> Project:

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("."),
        )
    )

    project.embedding_result = EmbeddingCollection(
        provider=EmbeddingProviderInfo(
            name="fake",
            model="test",
            dimensions=3,
        ),
        embeddings=[
            Embedding(
                chunk_id="chunk_auth",
                vector=[1.0, 0.0, 0.0],
            ),
            Embedding(
                chunk_id="chunk_database",
                vector=[0.0, 1.0, 0.0],
            ),
            Embedding(
                chunk_id="chunk_partial",
                vector=[0.8, 0.0, 0.0],
            ),
        ],
    )

    return project


def test_project_retrieval_returns_chunks() -> None:

    service = RetrievalService(
        Retriever()
    )

    result = service.retrieve_project(
        create_project(),
        RetrievalQuery(
            text="authentication",
        ),
        [1.0, 0.0, 0.0],
    )

    assert [
        item.chunk_id
        for item in result.results
    ] == [
        "chunk_auth",
        "chunk_partial",
        "chunk_database",
    ]


def test_project_embedding_state_is_not_modified() -> None:

    project = create_project()

    original_embeddings = project.embedding_result

    service = RetrievalService(
        Retriever()
    )

    service.retrieve_project(
        project,
        RetrievalQuery(
            text="authentication",
        ),
        [1.0, 0.0, 0.0],
    )

    assert project.embedding_result == original_embeddings


def test_project_without_embeddings_adds_diagnostic() -> None:

    project = Project(
        metadata=ProjectMetadata(
            name="empty-project",
            root_path=Path("."),
        )
    )

    service = RetrievalService(
        Retriever()
    )

    result = service.retrieve_project(
        project,
        RetrievalQuery(
            text="test",
        ),
        [1.0, 0.0, 0.0],
    )

    assert result.results == []

    assert project.diagnostics == [
        "Project has no embedding_result"
    ]