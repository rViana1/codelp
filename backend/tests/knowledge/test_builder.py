from pathlib import Path

from app.knowledge.builder import KnowledgeBuilder
from backend.core.project.models import (
    Project,
    ProjectMetadata,
)


def create_project():
    return Project(
        metadata=ProjectMetadata(
            name="codelp",
            root_path=Path("/tmp/codelp"),
        )
    )


def test_builder_creates_project_knowledge():

    builder = KnowledgeBuilder()

    project = create_project()

    knowledge = builder.build(
        project
    )

    assert knowledge.metadata.project_id == "codelp"


def test_builder_is_deterministic():

    builder = KnowledgeBuilder()

    project = create_project()

    first = builder.build(
        project
    )

    second = builder.build(
        project
    )

    assert (
        first.metadata.project_id
        ==
        second.metadata.project_id
    )


def test_builder_does_not_modify_project():

    builder = KnowledgeBuilder()

    project = create_project()

    original_name = project.metadata.name

    builder.build(
        project
    )

    assert project.metadata.name == original_name


def test_different_projects_have_different_identity():

    builder = KnowledgeBuilder()

    project_a = Project(
        metadata=ProjectMetadata(
            name="project-a",
            root_path=Path("/tmp/project-a"),
        )
    )

    project_b = Project(
        metadata=ProjectMetadata(
            name="project-b",
            root_path=Path("/tmp/project-b"),
        )
    )

    knowledge_a = builder.build(
        project_a
    )

    knowledge_b = builder.build(
        project_b
    )

    assert (
        knowledge_a.metadata.project_id
        !=
        knowledge_b.metadata.project_id
    )