from pathlib import Path

from core.project import (
    Project,
    ProjectMetadata,
)


def create_project():

    return Project(
        metadata=ProjectMetadata(
            name="runtime-project",
            root_path=Path("/tmp/project"),
        )
    )


def test_project_is_runtime_holder_of_analysis_results():

    project = create_project()


    assert project.parser_result is None
    assert project.index_result is None
    assert project.chunk_result is None
    assert project.embedding_result is None
    assert project.retrieval_result is None


def test_runtime_state_is_mutated_on_project():

    project = create_project()


    parser_state = object()

    project.parser_result = parser_state


    assert (
        project.parser_result
        is parser_state
    )