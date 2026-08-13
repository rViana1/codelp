from __future__ import annotations

from app.mcp.resources import (
    ContextResource,
    ProjectInformationResource,
    ProjectStructureResource,
    SymbolResource,
)

from app.mcp.server import MCPServer

from app.mcp.tools import (
    ContextRetrievalTool,
    MCPToolRegistry,
    SemanticSearchTool,
    SymbolLookupTool,
)

from app.mcp.models import MCPResourceDefinition, MCPToolDefinition


def create_mcp_server() -> MCPServer:
    """
    Creates and configures the MCP server.

    This function acts as the MCP composition root.

    It connects:
    - MCP server;
    - tools;
    - resources.

    It does not contain domain logic.
    """

    server = MCPServer()

    tool_registry = MCPToolRegistry()

    tools = [
        SymbolLookupTool(),
        ContextRetrievalTool(),
    ]

    for tool in tools:
        tool_registry.register(
            MCPToolDefinition(
                name=tool.name,
                description=tool.description,
            )
        )

        server.register_tool(
            MCPToolDefinition(
                name=tool.name,
                description=tool.description,
            )
        )

    resources = [
        ProjectInformationResource(),
        ProjectStructureResource(),
        ContextResource(),
    ]

    for resource in resources:
        server.register_resource(
            resource.definition()
        )

    return server
