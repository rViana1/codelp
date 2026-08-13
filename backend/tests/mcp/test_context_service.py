from app.mcp.context_service import ContextInformationService

from app.context.models import (
    ContextChunk,
    PromptContext,
)

from core.project.models import (
    Project,
    ProjectMetadata,
)

from pathlib import Path


def test_context_information_service_returns_context_information():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
    )

    project.context_result = PromptContext(
        query="authentication",
        context_id="context-123",
        chunks=[
            ContextChunk(
                chunk_id="chunk-1",
                content="def authenticate():",
                score=0.95,
            ),
        ],
        max_tokens=4000,
        total_tokens=10,
    )

    service = ContextInformationService()

    result = service.get_context(project)

    assert result == {
        "query": "authentication",
        "context_id": "context-123",
        "chunks": [
            {
                "chunk_id": "chunk-1",
                "content": "def authenticate():",
                "score": 0.95,
            },
        ],
        "max_tokens": 4000,
        "total_tokens": 10,
    }


def test_context_information_service_returns_none_without_context():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
    )

    service = ContextInformationService()

    result = service.get_context(project)

    assert result is None
