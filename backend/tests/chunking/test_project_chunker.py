from pathlib import Path

from app.chunking.chunker import ProjectChunker
from app.chunking.models import ChunkKind
from app.indexing.indexer import ProjectIndexer
from app.parser.parser import ProjectParser
from app.scanner.scanner import ProjectScanner
from core.project import Project, ProjectMetadata


def test_chunk_project_updates_domain_state(
    tmp_path: Path,
) -> None:

    (tmp_path / "src").mkdir()

    (tmp_path / "src" / "main.py").write_text(
        "def helper():\n"
        "    return 42\n\n"
        "class Service:\n"
        "    def run(self):\n"
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

    result = chunker.chunk_project(project)

    assert result is project

    assert project.chunk_result is not None

    chunks = project.chunk_result.chunks

    assert [chunk.id for chunk in chunks] == [
        "src/main.py::helper",
        "src/main.py::Service",
        "src/main.py::Service.run",
    ]

    class_chunk = chunks[1]

    assert class_chunk.kind == ChunkKind.CLASS

    assert class_chunk.content == (
        "class Service:\n"
        "    def run(self):\n"
        "        return True\n"
    )

    method_chunk = chunks[2]

    assert method_chunk.kind == ChunkKind.METHOD

    assert method_chunk.content == (
        "    def run(self):\n"
        "        return True\n"
    )

    function_chunk = chunks[0]

    assert function_chunk.kind == ChunkKind.FUNCTION

    assert function_chunk.content == (
        "def helper():\n"
        "    return 42\n"
    )

    assert project.diagnostics == []
