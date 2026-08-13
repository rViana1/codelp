from pathlib import Path

from app.mcp.context_service import ContextInformationService
from app.context.models import (
    ContextChunk,
    PromptContext,
)

from core.project.models import (
    Project,
    ProjectMetadata,
)


def test_context_preserves_chunk_identity():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
    )

    project.context_result = PromptContext(
        query="login",
        context_id="ctx-001",
        chunks=[
            ContextChunk(
                chunk_id="chunk-auth-001",
                content="login function",
                score=0.95,
            )
        ],
    )

    service = ContextInformationService()

    result = service.get_context(project)

    assert result["context_id"] == "ctx-001"

    assert (
        result["chunks"][0]["chunk_id"]
        == "chunk-auth-001"
    )
