from datetime import timezone
from pathlib import Path

from core.project import (
    Project,
    ProjectConfiguration,
    ProjectMetadata,
    ProjectStatistics,
)


def test_project_metadata_creation() -> None:

    metadata = ProjectMetadata(
        name="codelp",
        root_path=Path("/tmp/codelp"),
    )

    assert metadata.name == "codelp"
    assert metadata.root_path == Path("/tmp/codelp")
    assert metadata.description is None
    assert metadata.version is None


def test_project_metadata_uses_timezone_aware_utc() -> None:

    metadata = ProjectMetadata(
        name="codelp",
        root_path=Path("/tmp/codelp"),
    )

    assert metadata.created_at.tzinfo is not None
    assert metadata.created_at.tzinfo == timezone.utc

    assert metadata.last_updated.tzinfo is not None
    assert metadata.last_updated.tzinfo == timezone.utc


def test_project_configuration_defaults() -> None:

    configuration = ProjectConfiguration()

    assert configuration.follow_symlinks is False
    assert configuration.ignore_hidden is True
    assert configuration.max_file_size_bytes == 5 * 1024 * 1024
    assert configuration.ignored_directories == set()
    assert configuration.ignored_extensions == set()


def test_project_configuration_collections_are_not_shared() -> None:

    first = ProjectConfiguration()
    second = ProjectConfiguration()

    first.ignored_directories.add("node_modules")

    assert "node_modules" in first.ignored_directories
    assert "node_modules" not in second.ignored_directories


def test_project_statistics_defaults() -> None:

    statistics = ProjectStatistics()

    assert statistics.directories == 0
    assert statistics.files == 0
    assert statistics.scan_duration_seconds == 0.0


def test_project_creation() -> None:

    project = Project(
        metadata=ProjectMetadata(
            name="codelp",
            root_path=Path("/tmp/codelp"),
        )
    )

    assert project.metadata.name == "codelp"
    assert isinstance(project.configuration, ProjectConfiguration)
    assert isinstance(project.statistics, ProjectStatistics)

    assert project.root_tree is None
    assert project.parser_result is None
    assert project.index_result is None
    assert project.chunk_result is None
    assert project.embedding_result is None

    assert project.diagnostics == []


def test_project_diagnostics_are_not_shared() -> None:

    first = Project(
        metadata=ProjectMetadata(
            name="a",
            root_path=Path("/tmp/a"),
        )
    )

    second = Project(
        metadata=ProjectMetadata(
            name="b",
            root_path=Path("/tmp/b"),
        )
    )

    first.diagnostics.append("warning")

    assert first.diagnostics == ["warning"]
    assert second.diagnostics == []