from pathlib import Path

import pytest

from app.retrieval.models import RetrievalQuery
from app.runtime import (
    WorkspaceNotFoundError,
    WorkspaceState,
    create_codelp_application,
)
from app.configuration import CodelpSettings


def application(tmp_path: Path, *, embeddings: bool = True):
    return create_codelp_application(
        tmp_path / "knowledge",
        settings=CodelpSettings(
            embeddings={
                "enabled": embeddings,
                "provider": "local_hash" if embeddings else "disabled",
            }
        ),
    )


def project_root(tmp_path: Path) -> Path:
    root = tmp_path / "demo"
    root.mkdir()
    (root / "service.py").write_text(
        "def authenticate(user):\n    return bool(user)\n",
        encoding="utf-8",
    )
    return root


def test_runtime_opens_analyzes_understands_and_reports_status(tmp_path):
    runtime = application(tmp_path)
    workspace = runtime.open_project(project_root(tmp_path))

    assert workspace.state == WorkspaceState.OPEN
    project = runtime.analyze(workspace.workspace_id)
    status = runtime.status(workspace.workspace_id)

    assert project.knowledge_state is not None
    assert project.knowledge_state.graph is not None
    assert project.understanding_result is not None
    assert status.state == WorkspaceState.ANALYZED
    assert status.files == 1
    assert status.symbols == 1
    assert status.chunks == 1
    assert status.graph_entities > 0
    assert status.capabilities == {
        "analysis": True,
        "graph": True,
        "understanding": True,
        "retrieval": True,
        "llm": False,
    }


def test_runtime_coordinates_retrieval_context_and_exploration(tmp_path):
    runtime = application(tmp_path)
    workspace = runtime.open_project(project_root(tmp_path))
    project = runtime.analyze(workspace.workspace_id)

    result = runtime.retrieve(
        workspace.workspace_id,
        RetrievalQuery(text="authentication", limit=3),
        [1.0] * 8,
    )

    assert result.results
    assert project.retrieval_result == result
    assert project.context_result is not None
    assert project.context_result.chunks
    assert runtime.explore(
        workspace.workspace_id, "project"
    )["project_id"] == "demo"
    assert runtime.explore(
        workspace.workspace_id, "dependencies"
    ) == []


def test_runtime_reuses_persistent_knowledge_on_later_execution(tmp_path):
    root = project_root(tmp_path)
    runtime = application(tmp_path)
    first = runtime.open_project(root)
    first_project = runtime.analyze(first.workspace_id)
    file_id = first_project.knowledge_state.files[0].file_id
    runtime.close_project(first.workspace_id)

    second = runtime.open_project(root)
    second_project = runtime.analyze(second.workspace_id)

    assert second_project.knowledge_state.files[0].file_id == file_id
    assert second_project.incremental_analysis_result.full_analysis is False
    assert second_project.incremental_analysis_result.reused_files == (
        "service.py",
    )
    assert runtime.status(second.workspace_id).analysis_mode == "incremental"


def test_runtime_open_is_idempotent_and_close_releases_workspace(tmp_path):
    runtime = application(tmp_path)
    root = project_root(tmp_path)

    first = runtime.open_project(root)
    second = runtime.open_project(root)
    closed = runtime.close_project(first.workspace_id)

    assert first is second
    assert closed.state == WorkspaceState.CLOSED
    assert runtime.list_workspaces() == ()
    with pytest.raises(WorkspaceNotFoundError):
        runtime.status(first.workspace_id)


def test_runtime_rejects_missing_and_non_directory_roots(tmp_path):
    runtime = application(tmp_path)
    file_path = tmp_path / "source.py"
    file_path.write_text("pass\n", encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        runtime.open_project(tmp_path / "missing")
    with pytest.raises(NotADirectoryError):
        runtime.open_project(file_path)


def test_runtime_remains_useful_when_all_models_are_disabled(tmp_path):
    runtime = application(tmp_path, embeddings=False)
    workspace = runtime.open_project(project_root(tmp_path))

    project = runtime.analyze(workspace.workspace_id)
    status = runtime.status(workspace.workspace_id)

    assert project.index_result.symbols
    assert project.knowledge_state.graph is not None
    assert project.understanding_result is not None
    assert status.capabilities["retrieval"] is False
    assert status.capabilities["llm"] is False


def test_failed_public_execution_preserves_previous_committed_knowledge(
    tmp_path,
):
    root = project_root(tmp_path)
    runtime = application(tmp_path)
    workspace = runtime.open_project(root)
    runtime.analyze(workspace.workspace_id)
    snapshot = next(
        path
        for path in (tmp_path / "knowledge").glob("*.json")
        if not path.name.endswith(".analysis-cache.json")
    )
    previous = snapshot.read_bytes()

    runtime.analyzer.analyze = lambda _project: (_ for _ in ()).throw(
        OSError("simulated internal failure")
    )
    execution = runtime.submit_analysis(workspace.workspace_id)
    failed = runtime.wait_for_execution(execution.execution_id, 1)

    assert failed.state.value == "failed"
    assert failed.error_category == "internal_error"
    assert "simulated internal failure" not in (failed.error or "")
    assert snapshot.read_bytes() == previous
    assert runtime.status(workspace.workspace_id).state.value == "analyzed"


def test_multi_project_runtime_isolates_equal_directory_names(tmp_path):
    first_root = tmp_path / "first/demo"
    second_root = tmp_path / "second/demo"
    first_root.mkdir(parents=True)
    second_root.mkdir(parents=True)
    (first_root / "main.py").write_text("def first(): pass\n")
    (second_root / "main.py").write_text("def second(): pass\n")
    runtime = application(tmp_path)
    first = runtime.open_project(first_root)
    second = runtime.open_project(second_root)

    first_execution = runtime.submit_analysis(first.workspace_id)
    second_execution = runtime.submit_analysis(second.workspace_id)
    assert runtime.wait_for_execution(first_execution.execution_id, 2).state.value == (
        "completed"
    )
    assert runtime.wait_for_execution(second_execution.execution_id, 2).state.value == (
        "completed"
    )

    snapshots = [
        path
        for path in (tmp_path / "knowledge").glob("*.json")
        if not path.name.endswith(".analysis-cache.json")
    ]
    assert len(snapshots) == 2
    assert runtime.status(first.workspace_id).symbols == 1
    assert runtime.status(second.workspace_id).symbols == 1
    assert first.workspace_id != second.workspace_id
