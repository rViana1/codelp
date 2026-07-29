from pathlib import Path

from app.scanner.scanner import ProjectScanner
from core.project import Project, ProjectMetadata


def test_scan_project_updates_domain_state(tmp_path: Path) -> None:

    (tmp_path / "src").mkdir()

    (tmp_path / "src" / "main.py").write_text("print('hello')")

    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=tmp_path,
        )
    )

    scanner = ProjectScanner()

    result = scanner.scan_project(project)

    assert result is project

    assert project.statistics.files == 1

    assert project.statistics.directories == 1

    assert project.statistics.scan_duration_seconds >= 0

    assert project.root_tree is not None

    assert project.root_tree["name"] == tmp_path.name

    assert project.diagnostics == []
