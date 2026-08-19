"""Architecture acceptance rules for Milestone 11 Phase 1."""

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


def test_runtime_is_application_layer_and_core_does_not_depend_on_it():
    for path in (PROJECT_ROOT / "backend/core").rglob("*.py"):
        assert not any(
            imported.startswith("app.runtime")
            for imported in _imports(path)
        )


def test_runtime_uses_project_without_replacing_aggregate_root():
    source = (
        PROJECT_ROOT / "backend/app/runtime/application.py"
    ).read_text(encoding="utf-8")

    assert "Project(" in source
    assert "PersistentProjectKnowledge" not in source
    assert "FileKnowledgeStorage" not in source
    assert "knowledge_state" in Project.model_fields


def test_runtime_has_no_llm_dependency():
    for path in (PROJECT_ROOT / "backend/app/runtime").rglob("*.py"):
        imports = _imports(path)
        assert not any(
            "openai" in imported.lower()
            or "anthropic" in imported.lower()
            or imported.startswith("app.llm")
            for imported in imports
        )
