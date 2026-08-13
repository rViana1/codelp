from pathlib import Path

from app.mcp.resources import ProjectInformationResource
from core.project.models import (
    Project,
    ProjectMetadata,
    ProjectStatistics,
)


def test_project_information_resource_returns_project_information():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
        statistics=ProjectStatistics(
            scanned_files=[
                Path("src/main.py"),
                Path("README.md"),
            ],
        ),
    )

    resource = ProjectInformationResource()

    result = resource.read(project)

    assert result == {
        "name": "test-project",
        "root_path": "/tmp/test-project",
        "statistics": {
            "scanned_files": [
                "src/main.py",
                "README.md",
            ],
        },
    }


def test_project_information_resource_has_stable_uri():

    resource = ProjectInformationResource()

    assert resource.uri == "project://information"


def test_project_information_resource_definition():

    resource = ProjectInformationResource()

    definition = resource.definition()

    assert definition.uri == "project://information"
    assert (
        definition.description
        == "Provides public project information"
    )