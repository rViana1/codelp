"""Workspace scope and resource safety policy."""

from __future__ import annotations

import os
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
        max_project_files: int = 100000,
        max_project_bytes: int = 2 * 1024 * 1024 * 1024,
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
        self.max_project_files = max_project_files
        self.max_project_bytes = max_project_bytes

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

    def validate_project_budget(self, root: Path) -> None:
        files = 0
        size_bytes = 0
        excluded = {".git", ".codelp", ".venv", "venv", "node_modules"}
        for directory, directories, names in os.walk(root, followlinks=False):
            directories[:] = sorted(
                name
                for name in directories
                if name not in excluded
                and not (Path(directory) / name).is_symlink()
            )
            for name in sorted(names):
                path = Path(directory) / name
                try:
                    if path.is_symlink() or not path.is_file():
                        continue
                    files += 1
                    size_bytes += path.stat().st_size
                except OSError:
                    continue
                if files > self.max_project_files:
                    raise WorkspaceSecurityError(
                        "Project exceeds configured file-count limit"
                    )
                if size_bytes > self.max_project_bytes:
                    raise WorkspaceSecurityError(
                        "Project exceeds configured total-size limit"
                    )
