"""Executable architecture acceptance rules for Milestone 10.4 Phase 8."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path
from typing import get_args, get_type_hints

import pytest

from app.chunking.chunker import ProjectChunker
from app.embeddings.engine import EmbeddingEngine
from app.indexing.indexer import ProjectIndexer
from app.knowledge.identity import deterministic_identity
from app.parser.parser import ProjectParser
from app.scanner.scanner import ProjectScanner
from core.project import Project


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = PROJECT_ROOT / "backend"


def _python_files(relative_directory: str) -> list[Path]:
    return sorted((PROJECT_ROOT / relative_directory).rglob("*.py"))


def _tree(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _imports(path: Path) -> set[str]:
    result = set()
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)
    return result


def _defined_method_names(path: Path) -> set[str]:
    return {
        node.name
        for node in ast.walk(_tree(path))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def test_identity_tracking_and_incremental_logic_do_not_leak_into_core():
    """Core may carry state, but application decisions stay outside it."""

    forbidden_application_types = {
        "ChangeDetectionEngine",
        "FileIdentityDecision",
        "FileIdentityResolver",
        "IdentityTrackingEngine",
        "IdentityTrackingResult",
        "IncrementalAnalysisEngine",
        "KnowledgeAnalysisPlan",
        "KnowledgeExecutionPlanner",
        "KnowledgeUpdateEngine",
    }
    forbidden_logic_terms = (
        "detect_change",
        "incremental_analy",
        "plan_analysis",
        "resolve_identity",
        "track_identity",
    )

    for path in _python_files("backend/core"):
        imports = _imports(path)
        assert not any(name == "app" or name.startswith("app.") for name in imports), (
            f"{path} imports the application layer: {sorted(imports)}"
        )

        identifiers = {
            node.id
            for node in ast.walk(_tree(path))
            if isinstance(node, ast.Name)
        } | {
            node.attr
            for node in ast.walk(_tree(path))
            if isinstance(node, ast.Attribute)
        }
        leaked_types = forbidden_application_types & identifiers
        assert not leaked_types, f"{path} leaks application types: {leaked_types}"

        method_names = _defined_method_names(path)
        leaked_logic = {
            name
            for name in method_names
            if any(term in name.lower() for term in forbidden_logic_terms)
        }
        assert not leaked_logic, f"{path} owns application logic: {leaked_logic}"

    # These runtime slots deliberately remain opaque at the domain boundary.
    for field_name in (
        "knowledge_change_result",
        "incremental_analysis_result",
        "knowledge_analysis_plan",
    ):
        annotation = Project.model_fields[field_name].annotation
        assert set(get_args(annotation)) == {object, type(None)}


ANALYSIS_FACADES = {
    "backend/app/scanner/scanner.py": {
        "class": ProjectScanner,
        "public_methods": {"scan", "scan_project"},
        "forbidden_stages": (
            "app.parser",
            "app.indexing",
            "app.chunking",
            "app.embeddings",
        ),
    },
    "backend/app/parser/parser.py": {
        "class": ProjectParser,
        "public_methods": {"parse_file", "parse_project"},
        "forbidden_stages": (
            "app.scanner",
            "app.indexing",
            "app.chunking",
            "app.embeddings",
        ),
    },
    "backend/app/indexing/indexer.py": {
        "class": ProjectIndexer,
        "public_methods": {"build", "index_project"},
        "forbidden_stages": (
            "app.scanner",
            "app.chunking",
            "app.embeddings",
        ),
    },
    "backend/app/chunking/chunker.py": {
        "class": ProjectChunker,
        "public_methods": {"build", "chunk_project"},
        "forbidden_stages": (
            "app.scanner",
            "app.embeddings",
        ),
    },
    "backend/app/embeddings/engine.py": {
        "class": EmbeddingEngine,
        "public_methods": {"embed", "embed_project"},
        "forbidden_stages": (
            "app.scanner",
            "app.parser",
            "app.indexing",
        ),
    },
}


@pytest.mark.parametrize("relative_path", ANALYSIS_FACADES)
def test_analysis_facades_keep_their_single_responsibility(relative_path):
    contract = ANALYSIS_FACADES[relative_path]
    path = PROJECT_ROOT / relative_path
    imports = _imports(path)

    forbidden_boundaries = (
        "app.knowledge",
        "app.pipeline",
        "app.persistence",
        "app.storage",
    ) + contract["forbidden_stages"]
    violations = {
        imported
        for imported in imports
        if any(
            imported == forbidden or imported.startswith(f"{forbidden}.")
            for forbidden in forbidden_boundaries
        )
    }
    assert not violations, f"{relative_path} crosses boundaries: {violations}"

    facade = contract["class"]
    public_methods = {
        name
        for name, member in inspect.getmembers(facade, inspect.isfunction)
        if not name.startswith("_")
    }
    assert public_methods == contract["public_methods"]


@pytest.mark.parametrize(
    ("facade", "method_name"),
    [
        (ProjectScanner, "scan_project"),
        (ProjectParser, "parse_project"),
        (ProjectIndexer, "index_project"),
        (ProjectChunker, "chunk_project"),
        (EmbeddingEngine, "embed_project"),
    ],
)
def test_project_is_the_analysis_aggregate_root(facade, method_name):
    method = getattr(facade, method_name)
    hints = get_type_hints(method)

    assert hints["project"] is Project
    assert hints["return"] is Project


def test_knowledge_layer_owns_persistence_and_identity_intelligence():
    expected_owners = {
        "app/knowledge/tracking.py": "IdentityTrackingEngine",
        "app/knowledge/diff.py": "ChangeDetectionEngine",
        "app/knowledge/planning.py": "KnowledgeExecutionPlanner",
        "app/knowledge/update.py": "KnowledgeUpdateEngine",
        "app/knowledge/persistence.py": "KnowledgePersistenceService",
        "app/knowledge/lifecycle.py": "KnowledgeLifecycleService",
    }
    for relative_path, class_name in expected_owners.items():
        path = BACKEND_ROOT / relative_path
        class_names = {
            node.name
            for node in ast.walk(_tree(path))
            if isinstance(node, ast.ClassDef)
        }
        assert class_name in class_names, f"{class_name} moved out of Knowledge"

    forbidden_pipeline_internals = (
        "app.knowledge.diff",
        "app.knowledge.file_storage",
        "app.knowledge.hash",
        "app.knowledge.identity",
        "app.knowledge.mapper",
        "app.knowledge.models",
        "app.knowledge.persistence",
        "app.knowledge.storage",
        "app.knowledge.tracking",
        "app.knowledge.update",
    )
    for path in _python_files("backend/app/pipeline"):
        violations = {
            imported
            for imported in _imports(path)
            if any(
                imported == forbidden or imported.startswith(f"{forbidden}.")
                for forbidden in forbidden_pipeline_internals
            )
        }
        assert not violations, f"{path} owns persistence intelligence: {violations}"


def test_persistent_identity_generation_uses_deterministic_primitives():
    identity_sources = [
        BACKEND_ROOT / "app/knowledge/identity.py",
        BACKEND_ROOT / "app/knowledge/parser_mapper.py",
        BACKEND_ROOT / "app/knowledge/chunk_mapper.py",
    ]
    forbidden_imports = {"random", "secrets"}

    for path in identity_sources:
        tree = _tree(path)
        imports = _imports(path)
        assert not (imports & forbidden_imports)
        assert "uuid4" not in {
            node.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Name)
        }
        assert not any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "hash"
            for node in ast.walk(tree)
        ), f"{path} uses process-randomized built-in hash()"

    first = deterministic_identity("project", "file", "src/main.py", "abc")
    second = deterministic_identity("project", "file", "src/main.py", "abc")
    different = deterministic_identity("project", "file", "src/other.py", "abc")

    assert first == second
    assert first != different
