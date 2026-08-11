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

from core.project import (
    Project,
    ProjectMetadata,
)


def create_project() -> Project:

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=".",
        )
    )

    project.chunk_result = ChunkCollection(
        chunks=[
            CodeChunk(
                id="chunk_auth",
                file_path="auth.py",
                kind=ChunkKind.FUNCTION,
                content="def authenticate(): pass",
                start_line=1,
                end_line=1,
            )
        ]
    )

    project.retrieval_result = RetrievalCollection(
        query=RetrievalQuery(
            text="authentication",
        ),
        results=[
            RetrievalResult(
                chunk_id="chunk_auth",
                score=1.0,
            )
        ],
    )

    return project


def test_project_context_updates_domain_state():

    project = create_project()

    builder = ContextBuilder()

    builder.build_project(project)

    assert project.context_result is not None

    assert [
        chunk.chunk_id
        for chunk in project.context_result.chunks
    ] == [
        "chunk_auth"
    ]


def test_project_without_retrieval_adds_diagnostic():

    project = Project(
        metadata=ProjectMetadata(
            name="empty",
            root_path=".",
        )
    )

    builder = ContextBuilder()

    builder.build_project(project)

    assert project.diagnostics == [
        "Project has no retrieval_result"
    ]
