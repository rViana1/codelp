from pathlib import Path

from app.mcp.tools import SymbolLookupTool

from core.project.models import (
    Project,
    ProjectMetadata,
)


def test_symbol_lookup_returns_none_for_unknown_symbol():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
    )

    tool = SymbolLookupTool()

    result = tool.execute(
        project,
        "unknown-symbol",
    )

    assert result is None


def test_symbol_lookup_returns_none_without_index():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
    )

    tool = SymbolLookupTool()

    result = tool.execute(
        project,
        "",
    )

    assert result is None
