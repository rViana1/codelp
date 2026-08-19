"""Architecture acceptance rules for Milestone 10.5 Phase 4."""

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


def test_intelligent_retrieval_depends_on_runtime_contract_not_graph_builder():
    imports = _imports(
        PROJECT_ROOT / "backend/app/retrieval/intelligent.py"
    )

    assert "core.project" in imports
    assert not any(
        imported.startswith("app.knowledge")
        or imported.startswith("app.storage")
        or imported.startswith("app.vectorstore")
        for imported in imports
    )


def test_context_builder_does_not_implement_graph_traversal():
    imports = _imports(PROJECT_ROOT / "backend/app/context/builder.py")

    assert not any(
        imported.startswith("app.knowledge")
        or imported.endswith("retrieval.intelligent")
        for imported in imports
    )
