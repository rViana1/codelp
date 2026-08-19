from __future__ import annotations

from core.project.models import Project

from app.mcp.context_service import ContextInformationService
from app.mcp.models import MCPToolDefinition
from app.mcp.services import SymbolInformationService
from app.retrieval.models import (
    RetrievalCollection,
    RetrievalQuery,
)
from app.retrieval.service import RetrievalService
from app.understanding.service import ProjectKnowledgeService


class MCPToolRegistry:
    """
    Registry responsible for MCP tool definitions.

    This class does not execute tools.
    It only manages available tool contracts.
    """

    def __init__(self) -> None:
        self._tools: dict[str, MCPToolDefinition] = {}

    def register(
        self,
        tool: MCPToolDefinition,
    ) -> None:
        self._tools[tool.name] = tool

    def get(
        self,
        name: str,
    ) -> MCPToolDefinition | None:
        return self._tools.get(name)

    def list_tools(
        self,
    ) -> list[MCPToolDefinition]:
        return list(self._tools.values())


class SymbolLookupTool:
    """
    MCP tool responsible for symbol lookup.

    Delegates symbol retrieval to the application layer.
    """

    name = "symbol_lookup"

    description = (
        "Finds symbol information by symbol identifier."
    )

    def __init__(
        self,
        service: SymbolInformationService | None = None,
    ) -> None:
        self._service = (
            service
            or SymbolInformationService()
        )

    def execute(
        self,
        project: Project,
        symbol_id: str,
    ) -> dict[str, object] | None:
        return self._service.get_symbol(
            project,
            symbol_id,
        )


class SemanticSearchTool:
    """
    MCP tool responsible for semantic project search.

    Delegates retrieval to the retrieval application layer.
    """

    name = "semantic_search"

    description = (
        "Searches project knowledge using semantic retrieval."
    )

    def __init__(
        self,
        service: RetrievalService,
    ) -> None:
        self._service = service

    def execute(
        self,
        project: Project,
        query: RetrievalQuery,
        query_vector: list[float],
    ) -> RetrievalCollection:
        return self._service.retrieve_project(
            project,
            query,
            query_vector,
        )


class ContextRetrievalTool:
    """
    MCP tool responsible for retrieving
    structured project context.

    Delegates context access to the application layer.
    """

    name = "context_retrieval"

    description = (
        "Retrieves structured project context."
    )

    def __init__(
        self,
        service: ContextInformationService | None = None,
    ) -> None:
        self._service = (
            service
            or ContextInformationService()
        )

    def execute(
        self,
        project: Project,
    ) -> dict[str, object] | None:
        return self._service.get_context(
            project,
        )


class ProjectExplorationTool:
    """Explore project knowledge exclusively through an application service."""

    name = "project_exploration"
    description = (
        "Explores project graph, symbols, dependencies, history, related "
        "code and contextual knowledge."
    )

    def __init__(self, service: ProjectKnowledgeService | None = None) -> None:
        self._service = service or ProjectKnowledgeService()

    def execute(
        self,
        project: Project,
        view: str = "project",
        entity_id: str | None = None,
    ) -> object:
        if view == "project":
            return self._service.explore_project(project)
        if view == "symbol":
            return self._service.explore_symbol(project, entity_id or "")
        if view == "dependencies":
            return self._service.explore_dependencies(project, entity_id)
        if view == "history":
            return self._service.explore_history(project, entity_id)
        if view == "duplicates":
            return self._service.explore_duplicates(project, entity_id)
        if view == "similarity":
            return self._service.explore_similarity(project, entity_id)
        if view == "related_code":
            return self._service.explore_related_code(project, entity_id)
        if view == "context":
            return self._service.contextual_knowledge(project)
        raise ValueError(f"Unsupported project exploration view: {view}")
