"""Workspace scope and resource safety policy."""

from __future__ import annotations

from pathlib import Path


class WorkspaceSecurityError(PermissionError):
    pass


class WorkspaceSecurityPolicy:
    def __init__(
        self,
        allowed_roots: tuple[Path, ...],
        *,
        max_open_workspaces: int = 16,
        max_query_characters: int = 10000,
    ) -> None:
        roots = tuple(
            sorted(
                {path.expanduser().resolve() for path in allowed_roots},
                key=lambda item: item.as_posix(),
            )
        )
        if not roots:
            raise ValueError("At least one allowed project root is required")
        if any(path == Path(path.anchor) for path in roots):
            raise ValueError("Filesystem roots cannot be workspace allowlists")
        self.allowed_roots = roots
        self.max_open_workspaces = max_open_workspaces
        self.max_query_characters = max_query_characters

    def validate_project_root(self, root: Path) -> Path:
        resolved = root.expanduser().resolve()
        if not any(
            resolved == allowed or resolved.is_relative_to(allowed)
            for allowed in self.allowed_roots
        ):
            raise WorkspaceSecurityError(
                f"Project root is outside the configured workspace scope: {resolved}"
            )
        return resolved

    def validate_workspace_count(self, count: int) -> None:
        if count >= self.max_open_workspaces:
            raise WorkspaceSecurityError("Maximum open workspaces reached")

    def validate_query(self, text: str) -> None:
        if len(text) > self.max_query_characters:
            raise WorkspaceSecurityError("Query exceeds configured size limit")
