from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class WorkspaceOpenRequest(APIModel):
    path: str = Field(min_length=1, max_length=4096)
    name: str | None = None


class WorkspaceResponse(APIModel):
    workspace_id: str
    state: str


class QueryRequest(APIModel):
    text: str = Field(min_length=1, max_length=10000)
    limit: int = Field(default=5, ge=1, le=100)


class APIError(APIModel):
    code: str
    message: str
