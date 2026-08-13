from pathlib import Path

from app.mcp.tools import SymbolLookupTool
from app.indexing.models import (
    ProjectIndex,
    SymbolEntry,
    SymbolKind,
)
from core.project.models import (
    Project,
    ProjectMetadata,
)


def test_symbol_lookup_tool_returns_symbol_information():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
        index_result=ProjectIndex(
            symbols={
                "symbol-1": SymbolEntry(
                    id="symbol-1",
                    name="hello",
                    kind=SymbolKind.FUNCTION,
                    file_path="src/main.py",
                    qualified_name="main.hello",
                )
            }
        ),
    )

    tool = SymbolLookupTool()

    result = tool.execute(
        project,
        "symbol-1",
    )

    assert result == {
        "id": "symbol-1",
        "name": "hello",
        "kind": "function",
        "file_path": "src/main.py",
        "qualified_name": "main.hello",
    }


def test_symbol_lookup_tool_returns_none_when_symbol_not_found():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
    )

    tool = SymbolLookupTool()

    result = tool.execute(
        project,
        "missing",
    )

    assert result is None
