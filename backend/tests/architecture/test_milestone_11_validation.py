"""Consolidated Milestone 11 public-runtime architecture acceptance matrix."""

import ast
from pathlib import Path

from app.knowledge.interfaces import KnowledgeStorage
from core.project import Project


ROOT = Path(__file__).resolve().parents[3]


def imports(path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)
    return result


def test_project_remains_aggregate_and_runtime_is_application_only():
    assert "workspace_id" not in Project.model_fields
    assert "execution_manager" not in Project.model_fields
    for path in (ROOT / "backend/core").rglob("*.py"):
        assert not any(item.startswith("app.runtime") for item in imports(path))


def test_public_transports_depend_on_runtime_not_pipeline_or_storage():
    for relative in (
        "backend/app/cli/main.py",
        "backend/app/mcp/transport.py",
        "backend/app/api/application.py",
    ):
        values = imports(ROOT / relative)
        assert any(item.startswith("app.runtime") for item in values)
        assert not any(
            item.startswith("app.pipeline")
            or item.startswith("app.knowledge")
            for item in values
        )


def test_storage_remains_replaceable_and_llm_optional():
    assert KnowledgeStorage.__abstractmethods__ >= {
        "save", "load", "exists", "delete"
    }
    runtime_files = (ROOT / "backend/app/runtime").rglob("*.py")
    for path in runtime_files:
        values = imports(path)
        assert not any(
            item.startswith("openai")
            or item.startswith("anthropic")
            or item.startswith("app.llm")
            for item in values
        )
