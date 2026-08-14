from core.project.models import (
    Project,
    ProjectMetadata,
)

from app.knowledge.builder import KnowledgeBuilder


def create_project():
    return Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path="/tmp/test-project",
        )
    )


def test_builder_uses_mapper_flow():
    builder = KnowledgeBuilder()

    project = create_project()

    knowledge = builder.build(
        project
    )

    assert knowledge.metadata.project_id == "test-project"
