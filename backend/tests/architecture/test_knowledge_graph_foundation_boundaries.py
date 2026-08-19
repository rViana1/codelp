import ast
import inspect
from pathlib import Path
from typing import get_type_hints

from app.knowledge.graph import KnowledgeGraphBuilder
from app.knowledge.models import (
    PersistentKnowledgeGraph,
    PersistentProjectKnowledge,
)
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


def test_graph_builder_remains_inside_knowledge_representation_boundary():
    graph_module = PROJECT_ROOT / "backend/app/knowledge/graph.py"
    imports = _imports(graph_module)

    assert not any(
        imported.startswith("app.knowledge.storage")
        or imported.startswith("app.knowledge.file_storage")
        or imported.startswith("app.pipeline")
        for imported in imports
    )
    assert "knowledge" in inspect.signature(KnowledgeGraphBuilder.build).parameters
    hints = get_type_hints(KnowledgeGraphBuilder.build)
    assert hints["knowledge"] is PersistentProjectKnowledge
    assert hints["return"] is PersistentKnowledgeGraph


def test_graph_does_not_replace_project_aggregate_root():
    assert "graph" not in Project.model_fields
    assert "knowledge_state" in Project.model_fields


def test_analysis_components_do_not_depend_on_graph_implementation():
    for component in (
        "backend/app/scanner",
        "backend/app/parser",
        "backend/app/indexing",
        "backend/app/chunking",
        "backend/app/embeddings",
    ):
        for path in (PROJECT_ROOT / component).rglob("*.py"):
            assert "app.knowledge.graph" not in _imports(path)
