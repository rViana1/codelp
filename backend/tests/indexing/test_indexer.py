from pathlib import Path

from app.indexing.indexer import ProjectIndexer
from app.indexing.models import SymbolKind
from app.parser.models import (
    ClassSymbol,
    FunctionSymbol,
    ImportSymbol,
    MethodSymbol,
    ParsedFile,
    ParsedProject,
)


def test_build_empty_project() -> None:

    indexer = ProjectIndexer()

    index = indexer.build(
        Path("/project"),
        ParsedProject(),
    )

    assert index.files == {}

    assert index.symbols == {}

    assert index.dependencies == []


def test_index_single_function() -> None:

    parsed_project = ParsedProject(
        files=[
            ParsedFile(
                path=Path("/project/src/main.py"),
                language="python",
                functions=[
                    FunctionSymbol(name="hello"),
                ],
            )
        ]
    )

    indexer = ProjectIndexer()

    index = indexer.build(Path("/project"), parsed_project)

    symbol = index.symbols["src/main.py::hello"]

    assert symbol.kind == SymbolKind.FUNCTION

    assert symbol.qualified_name == "hello"

    assert index.files["src/main.py"].symbols == [
        "src/main.py::hello"
    ]


def test_index_single_class() -> None:

    parsed_project = ParsedProject(
        files=[
            ParsedFile(
                path=Path("/project/src/models.py"),
                language="python",
                classes=[
                    ClassSymbol(name="User"),
                ],
            )
        ]
    )

    indexer = ProjectIndexer()

    index = indexer.build(Path("/project"), parsed_project)

    symbol = index.symbols["src/models.py::User"]

    assert symbol.kind == SymbolKind.CLASS

    assert symbol.qualified_name == "User"


def test_index_single_method() -> None:

    parsed_project = ParsedProject(
        files=[
            ParsedFile(
                path=Path("/project/src/models.py"),
                language="python",
                classes=[
                    ClassSymbol(
                        name="User",
                        methods=[
                            MethodSymbol(
                                name="login",
                                class_name="User",
                            )
                        ],
                    )
                ],
            )
        ]
    )

    indexer = ProjectIndexer()

    index = indexer.build(Path("/project"), parsed_project)

    symbol = index.symbols["src/models.py::User.login"]

    assert symbol.kind == SymbolKind.METHOD

    assert symbol.qualified_name == "User.login"


def test_index_multiple_symbols() -> None:

    parsed_project = ParsedProject(
        files=[
            ParsedFile(
                path=Path("/project/src/main.py"),
                language="python",
                functions=[
                    FunctionSymbol(name="helper"),
                ],
                classes=[
                    ClassSymbol(
                        name="Service",
                        methods=[
                            MethodSymbol(
                                name="run",
                                class_name="Service",
                            )
                        ],
                    )
                ],
            )
        ]
    )

    indexer = ProjectIndexer()

    index = indexer.build(Path("/project"), parsed_project)

    assert list(index.symbols.keys()) == [
        "src/main.py::helper",
        "src/main.py::Service",
        "src/main.py::Service.run",
    ]


def test_index_dependencies() -> None:

    parsed_project = ParsedProject(
        files=[
            ParsedFile(
                path=Path("/project/src/main.py"),
                language="python",
                imports=[
                    ImportSymbol(module="os"),
                    ImportSymbol(module="pathlib"),
                ],
            )
        ]
    )

    indexer = ProjectIndexer()

    index = indexer.build(Path("/project"), parsed_project)

    assert index.files["src/main.py"].imports == [
        "os",
        "pathlib",
    ]

    assert len(index.dependencies) == 2

    assert index.dependencies[0].imported_module == "os"

    assert index.dependencies[1].imported_module == "pathlib"
