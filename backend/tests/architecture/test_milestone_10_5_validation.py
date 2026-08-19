"""Consolidated architecture acceptance matrix for Milestone 10.5 Phase 7."""

from __future__ import annotations

import ast
from pathlib import Path

from app.knowledge.graph import KnowledgeGraphBuilder
from app.knowledge.interfaces import KnowledgeStorage
from app.knowledge.validator import KnowledgeValidator
from core.project import Project, ProjectKnowledgeState
from tests.knowledge.test_knowledge_graph_relationships import (
    relationship_knowledge,
)


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


def test_project_remains_aggregate_root_and_graph_is_knowledge_state():
    assert "graph" not in Project.model_fields
    assert "knowledge_state" in Project.model_fields
    assert "graph" in ProjectKnowledgeState.model_fields


def test_core_domain_has_no_application_or_storage_dependencies():
    for path in (PROJECT_ROOT / "backend/core").rglob("*.py"):
        imports = _imports(path)
        assert not any(
            imported == "app"
            or imported.startswith("app.")
            or "storage" in imported
            for imported in imports
        ), f"{path} crosses the domain boundary"


def test_graph_persistence_remains_behind_storage_abstraction():
    assert KnowledgeStorage.__abstractmethods__ >= {
        "save", "load", "exists", "delete"
    }
    models_imports = _imports(
        PROJECT_ROOT / "backend/app/knowledge/models.py"
    )
    assert not any("storage" in item for item in models_imports)


def test_relationships_are_consistent_deterministic_and_historically_traceable():
    knowledge = relationship_knowledge()
    first = KnowledgeGraphBuilder().build(knowledge)
    second = KnowledgeGraphBuilder().build(
        knowledge.model_copy(
            update={
                "files": list(reversed(knowledge.files)),
                "symbols": list(reversed(knowledge.symbols)),
                "chunks": list(reversed(knowledge.chunks)),
                "imports": list(reversed(knowledge.imports)),
            },
            deep=True,
        )
    )
    candidate = knowledge.model_copy(update={"graph": first}, deep=True)

    KnowledgeValidator().validate(candidate)
    assert first == second
    entity_ids = {item.entity_id for item in first.entities}
    assert all(
        item.source_entity_id in entity_ids
        and item.target_entity_id in entity_ids
        for item in first.relationships
    )
    assert any(not item.is_current for item in first.entities)
    assert any(
        "moved" in item.kind.value or "renamed" in item.kind.value
        for item in first.relationships
    )


def test_retrieval_and_mcp_depend_only_on_public_application_contracts():
    retrieval_imports = _imports(
        PROJECT_ROOT / "backend/app/retrieval/intelligent.py"
    )
    assert not any(item.startswith("app.knowledge") for item in retrieval_imports)

    for path in (PROJECT_ROOT / "backend/app/mcp").rglob("*.py"):
        assert not any(
            item.startswith("app.knowledge") for item in _imports(path)
        ), f"{path} bypasses application services"
