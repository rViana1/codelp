from pathlib import Path

from app.context.models import (
    ContextChunk,
    PromptContext,
)

from app.mcp.resources import ContextResource

from core.project.models import (
    Project,
    ProjectMetadata,
)


def test_context_resource_returns_context_information():

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
                content="authenticate function",
                score=0.9,
            ),
        ],
    )

    resource = ContextResource()

    result = resource.read(project)

    assert result["context_id"] == "context-123"

    assert result["chunks"][0]["chunk_id"] == "chunk-1"


def test_context_resource_has_stable_uri():

    resource = ContextResource()

    assert resource.uri == "project://context"


def test_context_resource_definition():

    resource = ContextResource()

    definition = resource.definition()

    assert definition.uri == "project://context"

    assert (
        definition.description
        == "Provides structured project context information."
    )
