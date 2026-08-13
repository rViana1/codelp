from pathlib import Path

from app.mcp.resources import SymbolResource
from app.indexing.models import (
    ProjectIndex,
    SymbolEntry,
    SymbolKind,
)
from core.project.models import (
    Project,
    ProjectMetadata,
)


def test_symbol_resource_returns_symbol_information():

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

    resource = SymbolResource()

    result = resource.get(
        project,
        "src/user.py::User.login",
    )

    assert result["id"] == "src/user.py::User.login"
    assert result["qualified_name"] == "User.login"
