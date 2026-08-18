from pathlib import Path

from core.project import Project, ProjectMetadata


def test_project_contains_runtime_analysis_state():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/project"),
        )
    )


    assert hasattr(
        project,
        "parser_result",
    )

    assert hasattr(
        project,
        "index_result",
    )

    assert hasattr(
        project,
        "chunk_result",
    )

    assert hasattr(
        project,
        "embedding_result",
    )

    assert hasattr(
        project,
        "retrieval_result",
    )


def test_project_can_hold_knowledge_state():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/project"),
        )
    )


    assert hasattr(
        project,
        "knowledge_state",
    )