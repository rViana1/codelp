from pathlib import Path

from app.mcp.tools import SemanticSearchTool
from app.retrieval.models import RetrievalQuery
from app.retrieval.service import RetrievalService
from app.retrieval.retriever import Retriever
from app.vectorstore.manager import VectorStoreManager

from core.project.models import (
    Project,
    ProjectMetadata,
)


def test_semantic_search_propagates_missing_embedding_diagnostic():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
    )

    service = RetrievalService(
        retriever=Retriever(),
        store_manager=VectorStoreManager(),
    )

    tool = SemanticSearchTool(service)

    result = tool.execute(
        project,
        RetrievalQuery(
            text="authentication",
        ),
        [0.1, 0.2],
    )

    assert result.results == []

    assert (
        "Project has no embedding_result"
        in project.diagnostics
    )
