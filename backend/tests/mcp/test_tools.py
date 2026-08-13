from app.mcp.models import MCPToolDefinition
from app.mcp.tools import MCPToolRegistry


def test_tool_registry_registers_tools():
    registry = MCPToolRegistry()

    tool = MCPToolDefinition(
        name="symbol_lookup",
        description="Finds symbols",
    )

    registry.register(tool)

    assert registry.get("symbol_lookup") == tool


def test_tool_registry_lists_tools():
    registry = MCPToolRegistry()

    first = MCPToolDefinition(
        name="symbol_lookup",
        description="Finds symbols",
    )

    second = MCPToolDefinition(
        name="semantic_search",
        description="Searches project knowledge",
    )

    registry.register(first)
    registry.register(second)

    assert registry.list_tools() == [
        first,
        second,
    ]


def test_tool_registry_overwrites_tool_with_same_name():
    registry = MCPToolRegistry()

    first = MCPToolDefinition(
        name="symbol_lookup",
        description="Old",
    )

    second = MCPToolDefinition(
        name="symbol_lookup",
        description="New",
    )

    registry.register(first)
    registry.register(second)

    assert registry.get("symbol_lookup") == second
