from app.mcp.resources import MCPResourceRegistry
from app.mcp.models import MCPResourceDefinition


def test_resource_registry_returns_none_for_unavailable_resource():

    registry = MCPResourceRegistry()

    registry.register(
        MCPResourceDefinition(
            uri="project://information",
            description="Provides project information",
        )
    )

    result = registry.get(
        "project://unknown",
    )

    assert result is None


def test_resource_registry_returns_registered_resource():

    registry = MCPResourceRegistry()

    resource = MCPResourceDefinition(
        uri="project://information",
        description="Provides project information",
    )

    registry.register(resource)

    result = registry.get(
        "project://information",
    )

    assert result == resource
