from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class WorkspaceOpenRequest(APIModel):
    path: str = Field(min_length=1, max_length=4096)
    name: str | None = None


class WorkspaceResponse(APIModel):
    workspace_id: str
    state: str


class WorkspaceStatusResponse(APIModel):
    workspace_id: str
    project_name: str
    root_path: str
    state: str
    files: int
    directories: int
    symbols: int
    chunks: int
    embeddings: int
    graph_entities: int
    graph_relationships: int
    analysis_mode: str | None
    analyzed_files: tuple[str, ...]
    reused_files: tuple[str, ...]
    diagnostics: tuple[str, ...]
    capabilities: dict[str, bool]


class ExecutionResponse(APIModel):
    execution_id: str
    workspace_id: str
    state: str
    submitted_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    phase: str
    progress_percent: int
    error_category: str | None = None
    error: str | None = None


class QueryRequest(APIModel):
    text: str = Field(min_length=1, max_length=10000)
    limit: int = Field(default=5, ge=1, le=100)


class APIError(APIModel):
    code: str
    message: str
    category: str
