from __future__ import annotations

from enum import Enum

from app.mcp.models import (
    MCPResourceDefinition,
    MCPToolDefinition,
)

from app.mcp.execution import MCPToolExecutor

class MCPServerState(str, Enum):
    """
    Represents the lifecycle state of an MCP server.
    """

    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"


class MCPServer:
    """
    Minimal MCP server abstraction.

    This class manages:
    - server lifecycle;
    - tool registration;
    - resource registration.

    It does not implement transport handling
    or application/domain logic.
    """

    def __init__(self) -> None:
        self._state = MCPServerState.CREATED

        self._tools: dict[str, MCPToolDefinition] = {}
        self._resources: dict[str, MCPResourceDefinition] = {}
        self._executor = MCPToolExecutor()

    @property
    def state(self) -> MCPServerState:
        return self._state

    def initialize(self) -> None:
        """
        Initialize the MCP server.

        The server becomes available for external communication.
        """

        if self._state != MCPServerState.CREATED:
            return

        self._state = MCPServerState.RUNNING

    def shutdown(self) -> None:
        """
        Stop the MCP server lifecycle.
        """

        self._state = MCPServerState.STOPPED

    def register_tool(
        self,
        tool: MCPToolDefinition,
    ) -> None:
        self._tools[tool.name] = tool

    def register_resource(
        self,
        resource: MCPResourceDefinition,
    ) -> None:
        self._resources[resource.uri] = resource

    def tools(self) -> list[MCPToolDefinition]:
        return list(self._tools.values())

    def resources(self) -> list[MCPResourceDefinition]:
        return list(self._resources.values())
    
    def register_tool_implementation(
        self,
        tool: object,
    ) -> None:
        """
        Register executable MCP tool implementation.
        """

        self._executor.register(
            tool
        )
        
    def execute_tool(
        self,
        name: str,
        *args,
        **kwargs,
    ):
        """
        Execute registered MCP tool implementation.
        """

        return self._executor.execute(
            name,
            *args,
            **kwargs,
        )
        
    