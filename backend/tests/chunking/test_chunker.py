from pathlib import Path

from app.chunking.chunker import ProjectChunker
from app.chunking.models import ChunkKind
from app.indexing.indexer import ProjectIndexer
from app.parser.parser import ProjectParser
from app.scanner.scanner import ProjectScanner
from core.project import Project, ProjectMetadata


def test_chunk_empty_project(tmp_path: Path) -> None:

    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=tmp_path,
        )
    )

    scanner = ProjectScanner()
    scanner.scan_project(project)

    parser = ProjectParser()
    parser.parse_project(project)

    indexer = ProjectIndexer()
    indexer.index_project(project)

    chunker = ProjectChunker()

    result = chunker.build(
        tmp_path,
        project.parser_result,
        project.index_result,
    )

    assert result.chunks == []

    assert result.diagnostics == []


def test_chunk_single_function(tmp_path: Path) -> None:

    path = tmp_path / "main.py"

    path.write_text(
        "def hello():\n"
        "    return 42\n"
    )

    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=tmp_path,
        )
    )

    scanner = ProjectScanner()
    scanner.scan_project(project)

    parser = ProjectParser()
    parser.parse_project(project)

    indexer = ProjectIndexer()
    indexer.index_project(project)

    chunker = ProjectChunker()

    result = chunker.build(
        tmp_path,
        project.parser_result,
        project.index_result,
    )

    assert len(result.chunks) == 1

    chunk = result.chunks[0]

    assert chunk.id == "main.py::hello"

    assert chunk.kind == ChunkKind.FUNCTION

    assert chunk.content == (
        "def hello():\n"
        "    return 42\n"
    )


def test_chunk_single_method(tmp_path: Path) -> None:

    path = tmp_path / "main.py"

    path.write_text(
        "class User:\n"
        "    def login(self):\n"
        "        return True\n"
    )

    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=tmp_path,
        )
    )

    scanner = ProjectScanner()
    scanner.scan_project(project)

    parser = ProjectParser()
    parser.parse_project(project)

    indexer = ProjectIndexer()
    indexer.index_project(project)

    chunker = ProjectChunker()

    result = chunker.build(
        tmp_path,
        project.parser_result,
        project.index_result,
    )

    method_chunk = next(
        chunk
        for chunk in result.chunks
        if chunk.kind == ChunkKind.METHOD
    )

    assert method_chunk.id == "main.py::User.login"

    assert method_chunk.content == (
        "    def login(self):\n"
        "        return True\n"
    )


def test_chunk_single_class(tmp_path: Path) -> None:

    path = tmp_path / "main.py"

    path.write_text(
        "class User:\n"
        "    pass\n"
    )

    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=tmp_path,
        )
    )

    scanner = ProjectScanner()
    scanner.scan_project(project)

    parser = ProjectParser()
    parser.parse_project(project)

    indexer = ProjectIndexer()
    indexer.index_project(project)

    chunker = ProjectChunker()

    result = chunker.build(
        tmp_path,
        project.parser_result,
        project.index_result,
    )

    chunk = result.chunks[0]

    assert chunk.kind == ChunkKind.CLASS

    assert chunk.content == (
        "class User:\n"
        "    pass\n"
    )


def test_chunk_multiple_symbols_deterministic_order(
    tmp_path: Path,
) -> None:

    path = tmp_path / "main.py"

    path.write_text(
        "def b():\n"
        "    pass\n\n"
        "def a():\n"
        "    pass\n\n"
        "class User:\n"
        "    def z(self):\n"
        "        pass\n\n"
        "    def a(self):\n"
        "        pass\n"
    )

    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=tmp_path,
        )
    )

    scanner = ProjectScanner()
    scanner.scan_project(project)

    parser = ProjectParser()
    parser.parse_project(project)

    indexer = ProjectIndexer()
    indexer.index_project(project)

    chunker = ProjectChunker()

    result = chunker.build(
        tmp_path,
        project.parser_result,
        project.index_result,
    )

    assert [chunk.id for chunk in result.chunks] == [
        "main.py::a",
        "main.py::b",
        "main.py::User",
        "main.py::User.a",
        "main.py::User.z",
    ]
