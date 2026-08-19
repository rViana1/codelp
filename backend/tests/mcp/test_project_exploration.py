from app.mcp.bootstrap import create_mcp_server
from app.mcp.resources import ProjectKnowledgeResource
from app.mcp.tools import ProjectExplorationTool

from tests.understanding.test_project_knowledge_service import project


def test_project_knowledge_resource_delegates_to_application_service():
    result = ProjectKnowledgeResource().read(project())

    assert result["project_id"] == "demo"
    assert result["entity_counts"]["symbol"] == 1


def test_project_exploration_tool_exposes_supported_views():
    tool = ProjectExplorationTool()
    aggregate = project()

    assert tool.execute(aggregate, "symbol", "symbol-a")["entity_id"] == (
        "symbol-a"
    )
    assert tool.execute(aggregate, "dependencies", "file-a")[0]["kind"] == (
        "file_depends_on_file"
    )
    assert tool.execute(aggregate, "history", "file-a")[0]["kind"] == (
        "file_has_location"
    )
    assert tool.execute(aggregate, "similarity")[0]["kind"] == (
        "chunk_similar_to_chunk"
    )
    assert tool.execute(aggregate, "duplicates") == []


def test_bootstrap_exposes_and_executes_project_exploration():
    server = create_mcp_server()

    assert "project_exploration" in {item.name for item in server.tools()}
    assert "project://knowledge" in {item.uri for item in server.resources()}
    assert server.execute_tool("project_exploration", project())["project_id"] == (
        "demo"
    )
