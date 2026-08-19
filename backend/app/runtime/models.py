"""Application runtime models for managed project workspaces."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field

from core.project import Project


class WorkspaceState(str, Enum):
    OPEN = "open"
    ANALYZED = "analyzed"
    CLOSED = "closed"


@dataclass
class ProjectWorkspace:
    """Internal application session around one Project aggregate."""

    workspace_id: str
    project: Project
    state: WorkspaceState = WorkspaceState.OPEN
    opened_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    analyzed_at: datetime | None = None


class WorkspaceStatus(BaseModel):
    """Stable runtime status safe for public-interface translation."""

    workspace_id: str
    project_name: str
    root_path: str
    state: WorkspaceState
    files: int = 0
    directories: int = 0
    symbols: int = 0
    chunks: int = 0
    embeddings: int = 0
    graph_entities: int = 0
    graph_relationships: int = 0
    analysis_mode: str | None = None
    analyzed_files: tuple[str, ...] = ()
    reused_files: tuple[str, ...] = ()
    diagnostics: tuple[str, ...] = ()
    capabilities: dict[str, bool] = Field(default_factory=dict)
