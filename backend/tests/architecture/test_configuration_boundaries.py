"""Architecture acceptance rules for Milestone 11 Phase 2."""

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


def test_configuration_does_not_depend_on_transports_or_knowledge_storage():
    for path in (PROJECT_ROOT / "backend/app/configuration").rglob("*.py"):
        imports = _imports(path)
        assert not any(
            imported.startswith("app.cli")
            or imported.startswith("app.api")
            or imported.startswith("app.mcp")
            or imported.startswith("app.knowledge")
            for imported in imports
        )


def test_configuration_models_define_no_secret_value_fields():
    from app.configuration import CodelpSettings

    field_names = str(CodelpSettings.model_fields).lower()
    assert "api_key" not in field_names
    assert "token" not in field_names
    assert "password" not in field_names
