from app.indexing.models import (
    ProjectIndex,
    SymbolEntry,
    SymbolKind,
)

from app.mcp.server import MCPServer
from app.mcp.tools import SymbolLookupTool
from core.project.models import (
    Project,
    ProjectMetadata,
)

from pathlib import Path


def test_symbol_lookup_tool_through_server():

    symbol = SymbolEntry(
        id="user_service.login",
        name="login",
        kind=SymbolKind.METHOD,
        file_path="src/user.py",
        qualified_name="User.login",
    )

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
        index_result=ProjectIndex(
            symbols={
                "user_service.login": symbol,
            }
        ),
    )

    server = MCPServer()

    tool = SymbolLookupTool()

    server.register_tool_implementation(
        tool
    )

    result = server.execute_tool(
        "symbol_lookup",
        project,
        "user_service.login",
    )

    assert result == {
        "id": "user_service.login",
        "name": "login",
        "kind": "method",
        "file_path": "src/user.py",
        "qualified_name": "User.login",
    }