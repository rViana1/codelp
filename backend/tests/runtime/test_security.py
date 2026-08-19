from pathlib import Path

import pytest

from app.configuration import CodelpSettings
from app.runtime import (
    WorkspaceSecurityError,
    WorkspaceSecurityPolicy,
    create_codelp_application,
)


def test_workspace_policy_rejects_paths_outside_allowlist(tmp_path):
    allowed = tmp_path / "allowed"
    outside = tmp_path / "outside"
    allowed.mkdir()
    outside.mkdir()
    runtime = create_codelp_application(
        tmp_path / "knowledge",
        allowed_roots=(allowed,),
    )

    runtime.open_project(allowed)
    with pytest.raises(WorkspaceSecurityError, match="outside"):
        runtime.open_project(outside)


def test_workspace_policy_rejects_filesystem_root():
    with pytest.raises(ValueError, match="Filesystem roots"):
        WorkspaceSecurityPolicy((Path(Path.cwd().anchor),))


def test_workspace_and_query_limits_are_enforced(tmp_path):
    first = tmp_path / "one"
    second = tmp_path / "two"
    first.mkdir()
    second.mkdir()
    runtime = create_codelp_application(
        tmp_path / "knowledge",
        allowed_roots=(tmp_path,),
        settings=CodelpSettings(
            embeddings={"enabled": True, "provider": "local_hash"},
            security={"max_open_workspaces": 1, "max_query_characters": 4},
        ),
    )
    workspace = runtime.open_project(first)
    runtime.analyze(workspace.workspace_id)

    with pytest.raises(WorkspaceSecurityError, match="Maximum"):
        runtime.open_project(second)
    with pytest.raises(WorkspaceSecurityError, match="Query"):
        runtime.query(workspace.workspace_id, "12345")


def test_symlink_escape_resolves_outside_allowlist(tmp_path):
    allowed = tmp_path / "allowed"
    outside = tmp_path / "outside"
    allowed.mkdir()
    outside.mkdir()
    link = allowed / "escape"
    link.symlink_to(outside, target_is_directory=True)
    policy = WorkspaceSecurityPolicy((allowed,))

    with pytest.raises(WorkspaceSecurityError):
        policy.validate_project_root(link)
