from pathlib import Path

from app.context.models import (
    ContextChunk,
    PromptContext,
)

from app.mcp.tools import ContextRetrievalTool

from core.project.models import (
    Project,
    ProjectMetadata,
)


def test_context_retrieval_tool_returns_project_context():

    project = Project(
        metadata=ProjectMetadata(
            name="test-project",
            root_path=Path("/tmp/test-project"),
        ),
    )

    project.context_result = PromptContext(
        query="login",
        context_id="context-123",
        chunks=[
            ContextChunk(
                chunk_id="chunk-1",
                content="login implementation",
                score=0.95,
            ),
        ],
    )

    tool = ContextRetrievalTool()

    result = tool.execute(project)

    assert result["context_id"] == "context-123"

    assert (
        result["chunks"][0]["chunk_id"]
        == "chunk-1"
    )


def test_context_retrieval_tool_has_name():

    tool = ContextRetrievalTool()

    assert tool.name == "context_retrieval"
