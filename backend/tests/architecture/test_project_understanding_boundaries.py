"""Architecture acceptance rules for Milestone 10.5 Phase 3."""

from __future__ import annotations

import ast
from pathlib import Path

from core.project import Project


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)
    return result


def test_understanding_consumes_restored_graph_without_storage_dependency():
    engine = PROJECT_ROOT / "backend/app/understanding/engine.py"
    imports = _imports(engine)

    assert "core.project" in imports
    assert not any(
        imported.startswith("app.knowledge")
        or imported.startswith("app.persistence")
        or imported.startswith("app.storage")
        for imported in imports
    )


def test_understanding_remains_runtime_state_on_project_aggregate():
    field = Project.model_fields["understanding_result"]

    assert field.annotation == object | None
    assert "understanding_result" not in {
        "knowledge_state",
        "metadata",
    }


def test_knowledge_projection_does_not_depend_on_understanding_layer():
    knowledge_root = PROJECT_ROOT / "backend/app/knowledge"

    for path in knowledge_root.rglob("*.py"):
        assert not any(
            imported == "app.understanding"
            or imported.startswith("app.understanding.")
            for imported in _imports(path)
        ), f"{path} depends on a derived consumer layer"
