from app.mcp.models import (
    MCPResourceDefinition,
    MCPToolDefinition,
)
from app.mcp.server import MCPServer


def test_mcp_server_registers_tools():
    server = MCPServer()

    tool = MCPToolDefinition(
        name="project_info",
        description="Returns project information.",
    )

    server.register_tool(tool)

    assert server.tools() == [tool]


def test_mcp_server_registers_resources():
    server = MCPServer()

    resource = MCPResourceDefinition(
        uri="project://info",
        name="Project Information",
        description="Project metadata resource.",
    )

    server.register_resource(resource)

    assert server.resources() == [resource]


def test_mcp_server_overwrites_tool_with_same_name():
    server = MCPServer()

    first = MCPToolDefinition(
        name="search",
        description="First definition.",
    )

    second = MCPToolDefinition(
        name="search",
        description="Updated definition.",
    )

    server.register_tool(first)
    server.register_tool(second)

    assert server.tools() == [second]
