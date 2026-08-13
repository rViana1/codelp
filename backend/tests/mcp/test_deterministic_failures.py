from pathlib import Path

from app.mcp.context_service import ContextInformationService
from app.mcp.services import SymbolInformationService

from app.retrieval.models import RetrievalQuery
from app.retrieval.retriever import Retriever
from app.retrieval.service import RetrievalService

from app.vectorstore.manager import VectorStoreManager

from core.project.models import (
    Project,
    ProjectMetadata,
)


def create_empty_project():

    return Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
    )


def test_context_failure_is_deterministic():

    project = create_empty_project()

    service = ContextInformationService()

    first = service.get_context(project)
    second = service.get_context(project)

    assert first is None
    assert second is None


def test_symbol_lookup_failure_is_deterministic():

    project = create_empty_project()

    service = SymbolInformationService()

    first = service.get_symbol(
        project,
        "missing",
    )

    second = service.get_symbol(
        project,
        "missing",
    )

    assert first is None
    assert second is None


def test_retrieval_failure_is_deterministic():

    project = create_empty_project()

    service = RetrievalService(
        retriever=Retriever(),
        store_manager=VectorStoreManager(),
    )

    query = RetrievalQuery(
        text="test",
    )

    first = service.retrieve_project(
        project,
        query,
        [0.1, 0.2],
    )

    second = service.retrieve_project(
        project,
        query,
        [0.1, 0.2],
    )

    assert first.results == []
    assert second.results == []

    assert first.query == second.query

    assert project.diagnostics.count(
        "Project has no embedding_result"
    ) == 2
