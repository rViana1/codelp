from pathlib import Path

from app.parser.parser import ProjectParser
from app.scanner.scanner import ProjectScanner
from core.project import Project, ProjectMetadata


def test_parse_project_updates_domain_state(tmp_path: Path) -> None:

    (tmp_path / "src").mkdir()

    (tmp_path / "src" / "main.py").write_text(
        "import os\n\n"
        "def hello():\n"
        "    pass\n"
    )

    (tmp_path / "README.md").write_text("# Demo")

    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=tmp_path,
        )
    )

    scanner = ProjectScanner()

    scanner.scan_project(project)

    parser = ProjectParser()

    result = parser.parse_project(project)

    assert result is project

    assert project.parser_result is not None

    assert len(project.parser_result.files) == 1

    parsed_file = project.parser_result.files[0]

    assert parsed_file.path.name == "main.py"

    assert parsed_file.language == "python"

    assert len(parsed_file.imports) == 1

    assert parsed_file.imports[0].module == "os"

    assert len(parsed_file.functions) == 1

    assert parsed_file.functions[0].name == "hello"

    assert project.parser_result.diagnostics == [
        f"Unsupported language: {tmp_path / 'README.md'}"
    ]

    assert project.diagnostics == [
        f"Unsupported language: {tmp_path / 'README.md'}"
    ]
