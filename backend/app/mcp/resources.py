from __future__ import annotations

from core.project.models import Project

from app.mcp.context_service import ContextInformationService
from app.mcp.models import MCPResourceDefinition
from app.mcp.services import (
    ProjectInformationService,
    ProjectStructureService,
    SymbolInformationService,
)
from app.understanding.service import ProjectKnowledgeService


class MCPResourceRegistry:
    """
    Registry responsible for MCP resource definitions.

    This class only manages resource contracts.
    It does not execute resource logic.
    """

    def __init__(self) -> None:
        self._resources: dict[str, MCPResourceDefinition] = {}

    def register(
        self,
        resource: MCPResourceDefinition,
    ) -> None:
        self._resources[resource.uri] = resource

    def get(
        self,
        uri: str,
    ) -> MCPResourceDefinition | None:
        return self._resources.get(uri)

    def list_resources(
        self,
    ) -> list[MCPResourceDefinition]:
        return list(self._resources.values())


class ProjectInformationResource:
    """
    MCP resource exposing public project information.
    """

    uri = "project://information"

    def __init__(
        self,
        service: ProjectInformationService | None = None,
    ) -> None:
        self._service = (
            service
            or ProjectInformationService()
        )

    def read(
        self,
        project: Project,
    ) -> dict[str, object]:
        return self._service.get_information(project)

    def definition(
        self,
    ) -> MCPResourceDefinition:
        return MCPResourceDefinition(
            uri=self.uri,
            description="Provides public project information",
        )


class ProjectStructureResource:
    """
    MCP resource exposing project structure information.
    """

    uri = "project://structure"

    def __init__(
        self,
        service: ProjectStructureService | None = None,
    ) -> None:
        self._service = (
            service
            or ProjectStructureService()
        )

    def read(
        self,
        project: Project,
    ) -> dict[str, object]:
        return self._service.get_structure(project)

    def definition(
        self,
    ) -> MCPResourceDefinition:
        return MCPResourceDefinition(
            uri=self.uri,
            description="Provides project structure information",
        )


class SymbolResource:
    """
    MCP resource exposing project symbols.
    """

    uri = "project://symbols"

    def __init__(
        self,
        service: SymbolInformationService | None = None,
    ) -> None:
        self._service = (
            service
            or SymbolInformationService()
        )

    def get(
        self,
        project: Project,
        symbol_id: str,
    ) -> dict[str, object] | None:
        return self._service.get_symbol(
            project,
            symbol_id,
        )

    def definition(
        self,
    ) -> MCPResourceDefinition:
        return MCPResourceDefinition(
            uri=self.uri,
            description="Provides project symbol information.",
        )


class ContextResource:
    """
    MCP resource exposing structured project context.
    """

    uri = "project://context"

    description = (
        "Provides structured project context information."
    )

    def __init__(
        self,
        service: ContextInformationService | None = None,
    ) -> None:
        self._service = (
            service
            or ContextInformationService()
        )

    def read(
        self,
        project: Project,
    ) -> dict[str, object] | None:
        return self._service.get_context(project)

    def definition(
        self,
    ) -> MCPResourceDefinition:
        return MCPResourceDefinition(
            uri=self.uri,
            description=self.description,
        )


class ProjectKnowledgeResource:
    """MCP resource exposing a safe project knowledge overview."""

    uri = "project://knowledge"

    def __init__(self, service: ProjectKnowledgeService | None = None) -> None:
        self._service = service or ProjectKnowledgeService()

    def read(self, project: Project) -> dict[str, object]:
        return self._service.explore_project(project)

    def definition(self) -> MCPResourceDefinition:
        return MCPResourceDefinition(
            uri=self.uri,
            description=(
                "Provides project graph, relationship and history knowledge."
            ),
        )
