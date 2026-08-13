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


def test_semantic_search_tool_preserves_chunk_identity():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
        embedding_result=EmbeddingCollection(
            provider=EmbeddingProviderInfo(
                name="test",
                model="test-model",
                dimensions=2,
            ),
            embeddings=[
                Embedding(
                    chunk_id="chunk-1",
                    vector=[1.0, 0.0],
                ),
                Embedding(
                    chunk_id="chunk-2",
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

    assert result.results[0].chunk_id == "chunk-1"


def test_semantic_search_tool_preserves_retrieval_order():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
        embedding_result=EmbeddingCollection(
            provider=EmbeddingProviderInfo(
                name="test",
                model="test-model",
                dimensions=2,
            ),
            embeddings=[
                Embedding(
                    chunk_id="chunk-b",
                    vector=[0.0, 1.0],
                ),
                Embedding(
                    chunk_id="chunk-a",
                    vector=[1.0, 0.0],
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
            text="test",
            limit=2,
        ),
        [1.0, 0.0],
    )

    assert [
        item.chunk_id
        for item in result.results
    ] == [
        "chunk-a",
        "chunk-b",
    ]
