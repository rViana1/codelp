from pathlib import Path

from core.project import Project
from core.project.models import ProjectMetadata

from app.indexing.models import (
    ProjectIndex,
    SymbolEntry,
    SymbolKind,
)

from app.knowledge.builder import KnowledgeBuilder


def test_builder_persists_index_symbols():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        )
    )

    project.index_result = ProjectIndex(
        symbols={
            "symbol-1": SymbolEntry(
                id="symbol-1",
                name="hello",
                kind=SymbolKind.FUNCTION,
                file_path="main.py",
                qualified_name="hello",
            )
        }
    )

    knowledge = KnowledgeBuilder().build(
        project
    )

    assert any(
        symbol.name == "hello"
        for symbol in knowledge.symbols
    )
