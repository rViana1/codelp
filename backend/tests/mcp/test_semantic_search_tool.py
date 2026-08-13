from pathlib import Path

from core.project.models import (
    Project,
    ProjectMetadata,
)

from app.embeddings.models import (
    Embedding,
    EmbeddingCollection,
    EmbeddingProviderInfo,
)

from app.mcp.tools import SemanticSearchTool

from app.retrieval.models import RetrievalQuery
from app.retrieval.retriever import Retriever
from app.retrieval.service import RetrievalService

from app.vectorstore.manager import VectorStoreManager


def test_semantic_search_tool_returns_ranked_results():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
        embedding_result=EmbeddingCollection(
            provider=EmbeddingProviderInfo(
                name="test-provider",
                model="test-model",
                dimensions=2,
            ),
            embeddings=[
                Embedding(
                    chunk_id="chunk_a",
                    vector=[1.0, 0.0],
                ),
                Embedding(
                    chunk_id="chunk_b",
                    vector=[0.0, 1.0],
                ),
            ],
        ),
    )

    retrieval_service = RetrievalService(
        retriever=Retriever(),
        store_manager=VectorStoreManager(),
    )

    tool = SemanticSearchTool(
        service=retrieval_service,
    )

    result = tool.execute(
        project,
        RetrievalQuery(
            text="authentication",
            limit=2,
        ),
        [1.0, 0.0],
    )

    assert result.query.text == "authentication"

    assert result.results[0].chunk_id == "chunk_a"

    assert result.results[0].score >= result.results[1].score