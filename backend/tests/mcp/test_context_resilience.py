from pathlib import Path

from app.mcp.context_service import ContextInformationService

from core.project.models import (
    Project,
    ProjectMetadata,
)


def test_context_service_handles_missing_context():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
    )

    service = ContextInformationService()

    result = service.get_context(project)

    assert result is None
