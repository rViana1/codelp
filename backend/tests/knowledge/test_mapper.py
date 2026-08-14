from pathlib import Path

from core.project.models import (
    Project,
    ProjectMetadata,
    ProjectStatistics,
)

from app.knowledge.mapper import KnowledgeMapper


def create_project():
    return Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
        statistics=ProjectStatistics(
            scanned_files=[
                Path("src/main.py"),
                Path("src/models.py"),
            ]
        ),
    )


def test_mapper_creates_project_knowledge():
    project = create_project()

    knowledge = KnowledgeMapper.from_project(project)

    assert knowledge.metadata.project_id == "test-project"
    assert len(knowledge.files) == 2


def test_mapper_does_not_modify_project():
    project = create_project()

    original_files = list(
        project.statistics.scanned_files
    )

    KnowledgeMapper.from_project(project)

    assert project.statistics.scanned_files == original_files
