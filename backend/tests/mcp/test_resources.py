from app.mcp.models import MCPResourceDefinition
from app.mcp.resources import MCPResourceRegistry


def test_resource_registry_registers_resources():
    registry = MCPResourceRegistry()

    resource = MCPResourceDefinition(
        uri="project://information",
        description="Provides project information",
    )

    registry.register(resource)

    assert registry.get("project://information") == resource


def test_resource_registry_lists_resources():
    registry = MCPResourceRegistry()

    first = MCPResourceDefinition(
        uri="project://information",
        description="Provides project information",
    )

    second = MCPResourceDefinition(
        uri="project://structure",
        description="Provides project structure",
    )

    registry.register(first)
    registry.register(second)

    assert registry.list_resources() == [
        first,
        second,
    ]


def test_resource_registry_overwrites_resource_with_same_uri():
    registry = MCPResourceRegistry()

    first = MCPResourceDefinition(
        uri="project://information",
        description="Old description",
    )

    second = MCPResourceDefinition(
        uri="project://information",
        description="New description",
    )

    registry.register(first)
    registry.register(second)

    assert registry.get("project://information") == second