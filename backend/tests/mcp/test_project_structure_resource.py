from pathlib import Path

from app.mcp.resources import ProjectStructureResource
from core.project.models import (
    Project,
    ProjectMetadata,
)


def test_project_structure_resource_returns_tree():
    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
        root_tree={
            "name": "test-project",
            "children": [
                {
                    "name": "main.py",
                    "type": "file",
                }
            ],
        },
    )

    resource = ProjectStructureResource()

    result = resource.read(project)

    assert result == {
        "root_tree": {
            "name": "test-project",
            "children": [
                {
                    "name": "main.py",
                    "type": "file",
                }
            ],
        },
    }


def test_project_structure_resource_has_stable_uri():
    resource = ProjectStructureResource()

    assert resource.uri == "project://structure"


def test_project_structure_resource_definition():
    resource = ProjectStructureResource()

    definition = resource.definition()

    assert definition.uri == "project://structure"
    assert (
        definition.description
        == "Provides project structure information"
    )
