from pathlib import Path

from core.project.models import (
    Project,
    ProjectMetadata,
)

from app.mcp.resources import (
    ProjectInformationResource,
)


def test_project_information_resource_serializes_deterministically():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
    )

    resource = ProjectInformationResource()

    first = resource.read(project)
    second = resource.read(project)

    assert first == second

    assert first["name"] == "test-project"

    assert (
        first["root_path"]
        == "/tmp/test-project"
    )
