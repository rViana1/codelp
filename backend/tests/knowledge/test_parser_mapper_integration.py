from pathlib import Path

from core.project import Project
from core.project.models import (
    ProjectMetadata,
)

from app.knowledge.builder import KnowledgeBuilder

from app.parser.models import (
    ParsedProject,
    ParsedFile,
    FunctionSymbol,
)


def test_builder_persists_parser_symbols():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        )
    )

    project.parser_result = ParsedProject(
        files=[
            ParsedFile(
                path=Path("main.py"),
                language="python",
                functions=[
                    FunctionSymbol(
                        name="hello",
                        start_line=1,
                        end_line=2,
                    )
                ],
            )
        ]
    )

    knowledge = KnowledgeBuilder().build(
        project
    )

    assert len(
        knowledge.symbols
    ) == 1

    assert (
        knowledge.symbols[0].name
        == "hello"
    )

    assert (
        knowledge.symbols[0].symbol_type
        == "function"
    )
