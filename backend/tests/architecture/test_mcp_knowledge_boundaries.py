"""Architecture acceptance rules for Milestone 10.5 Phase 5."""

import ast
from pathlib import Path


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


def test_mcp_does_not_bypass_project_knowledge_application_service():
    for path in (PROJECT_ROOT / "backend/app/mcp").rglob("*.py"):
        imports = _imports(path)
        assert not any(
            imported.startswith("app.knowledge")
            or imported.startswith("app.storage")
            for imported in imports
        ), f"{path} bypasses the project knowledge application service"


def test_project_knowledge_service_is_independent_from_mcp_and_storage():
    imports = _imports(
        PROJECT_ROOT / "backend/app/understanding/service.py"
    )

    assert "core.project" in imports
    assert not any(
        imported.startswith("app.mcp")
        or imported.startswith("app.knowledge")
        or imported.startswith("app.storage")
        for imported in imports
    )
