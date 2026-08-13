from pathlib import Path

from core.project.models import (
    Project,
    ProjectMetadata,
    ProjectStatistics,
)
from app.mcp.services import ProjectInformationService


def test_project_information_service_returns_public_information():
    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
        statistics=ProjectStatistics(
            scanned_files=[
                "src/main.py",
                "src/models/user.py",
                "src/services/auth.py",
                "tests/test_main.py",
                "README.md",
            ],
        ),
    )

    service = ProjectInformationService()

    result = service.get_information(project)

    assert result == {
        "name": "test-project",
        "root_path": "/tmp/test-project",
        "statistics": {
            "scanned_files": [
                "src/main.py",
                "src/models/user.py",
                "src/services/auth.py",
                "tests/test_main.py",
                "README.md",
            ],
        },
    }