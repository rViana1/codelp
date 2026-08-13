from pathlib import Path

from app.mcp.services import SymbolInformationService
from app.indexing.models import ProjectIndex, SymbolEntry, SymbolKind
from core.project.models import (
    Project,
    ProjectMetadata,
)


def test_symbol_information_service_returns_symbol_information():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
        index_result=ProjectIndex(
            symbols={
                "src/user.py::User.login": SymbolEntry(
                    id="src/user.py::User.login",
                    name="login",
                    kind=SymbolKind.METHOD,
                    file_path="src/user.py",
                    qualified_name="User.login",
                )
            }
        ),
    )

    service = SymbolInformationService()

    result = service.get_symbol(
        project,
        "src/user.py::User.login",
    )

    assert result == {
        "id": "src/user.py::User.login",
        "name": "login",
        "kind": "method",
        "file_path": "src/user.py",
        "qualified_name": "User.login",
    }
