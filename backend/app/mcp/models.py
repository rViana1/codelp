from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MCPRequest(BaseModel):
    """
    Generic MCP request model.
    """

    method: str
    params: dict[str, Any] = Field(default_factory=dict)


class MCPResponse(BaseModel):
    """
    Generic MCP response model.
    """

    result: dict[str, Any] | None = None
    error: str | None = None


class MCPToolDefinition(BaseModel):
    """
    Definition of an MCP tool exposed by the server.
    """

    name: str
    description: str
    input_schema: dict[str, Any] = Field(
        default_factory=dict
    )


class MCPResourceDefinition(BaseModel):
    """
    Definition of an MCP resource exposed by the server.
    """

    uri: str
    description: str


class MCPProjectInformation(BaseModel):
    """
    Public project information exposed through MCP.
    """

    name: str
    root_path: str
    statistics: dict[str, Any]


class MCPToolRequest(BaseModel):
    """
    Base model for MCP tool requests.
    """

    parameters: dict[str, Any] = Field(
        default_factory=dict
    )


class MCPToolResponse(BaseModel):
    """
    Base response model for MCP tools.
    """

    success: bool
    data: dict[str, Any] = Field(
        default_factory=dict
    )
    diagnostics: list[str] = Field(
        default_factory=list
    )

class MCPRetrievalResult(BaseModel):
    """
    MCP representation of a retrieved knowledge item.
    """

    chunk_id: str
    score: float


class MCPRetrievalResponse(BaseModel):
    """
    MCP response containing deterministic retrieval results.
    """

    query: str

    results: list[MCPRetrievalResult] = Field(
        default_factory=list
    )