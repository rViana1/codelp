from pathlib import Path

from app.indexing.indexer import ProjectIndexer
from app.parser.parser import ProjectParser
from app.scanner.scanner import ProjectScanner
from core.project import Project, ProjectMetadata


def test_index_project_updates_domain_state(tmp_path: Path) -> None:

    (tmp_path / "src").mkdir()

    (tmp_path / "src" / "main.py").write_text(
        "import os\n\n"
        "def helper():\n"
        "    pass\n\n"
        "class Service:\n"
        "    def run(self):\n"
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

    result = indexer.index_project(project)

    assert result is project

    assert project.index_result is not None

    assert list(project.index_result.files.keys()) == [
        "src/main.py"
    ]

    assert list(project.index_result.symbols.keys()) == [
        "src/main.py::helper",
        "src/main.py::Service",
        "src/main.py::Service.run",
    ]

    file_entry = project.index_result.files["src/main.py"]

    assert file_entry.imports == ["os"]

    assert file_entry.symbols == [
        "src/main.py::helper",
        "src/main.py::Service",
        "src/main.py::Service.run",
    ]

    assert len(project.index_result.dependencies) == 1

    dependency = project.index_result.dependencies[0]

    assert dependency.source_file == "src/main.py"

    assert dependency.imported_module == "os"

    assert project.diagnostics == []
