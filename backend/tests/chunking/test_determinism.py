from pathlib import Path

from app.chunking.chunker import ProjectChunker
from app.indexing.indexer import ProjectIndexer
from app.parser.parser import ProjectParser
from app.scanner.scanner import ProjectScanner
from core.project import Project, ProjectMetadata


def build_chunks(root: Path) -> list[str]:

    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=root,
        )
    )

    scanner = ProjectScanner()
    scanner.scan_project(project)

    parser = ProjectParser()
    parser.parse_project(project)

    indexer = ProjectIndexer()
    indexer.index_project(project)

    chunker = ProjectChunker()
    chunker.chunk_project(project)

    return [chunk.id for chunk in project.chunk_result.chunks]


def test_chunk_ids_are_stable(tmp_path: Path) -> None:

    (tmp_path / "main.py").write_text(
        "def hello():\n"
        "    pass\n"
    )

    first = build_chunks(tmp_path)
    second = build_chunks(tmp_path)

    assert first == second


def test_chunk_order_is_deterministic(tmp_path: Path) -> None:

    (tmp_path / "main.py").write_text(
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

    result = build_chunks(tmp_path)

    assert result == [
        "main.py::a",
        "main.py::b",
        "main.py::User",
        "main.py::User.a",
        "main.py::User.z",
    ]
