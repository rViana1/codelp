from pathlib import Path

from core.project.models import (
    Project,
    ProjectConfiguration,
    ProjectMetadata,
)

from app.knowledge.mapper import KnowledgeMapper


def test_project_configuration_is_persisted():
    project = Project(
        metadata=ProjectMetadata(
            name="project",
            root_path=Path("/tmp/project"),
        ),
        configuration=ProjectConfiguration(
            follow_symlinks=True,
            ignore_hidden=False,
            max_file_size_bytes=123456,
            ignored_directories={
                ".git",
                "node_modules",
            },
            ignored_extensions={
                ".tmp",
                ".log",
            },
        ),
    )

    knowledge = KnowledgeMapper.from_project(
        project
    )

    assert knowledge.configuration.follow_symlinks is True

    assert knowledge.configuration.ignore_hidden is False

    assert (
        knowledge.configuration.max_file_size_bytes
        == 123456
    )

    assert knowledge.configuration.ignored_directories == {
        ".git",
        "node_modules",
    }

    assert knowledge.configuration.ignored_extensions == {
        ".tmp",
        ".log",
    }
