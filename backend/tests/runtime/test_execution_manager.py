import threading

import pytest

from app.runtime import (
    AnalysisExecutionManager,
    ExecutionConflictError,
    ExecutionState,
    ExecutionTimeoutError,
)


def test_execution_identity_state_and_workspace_conflict():
    release = threading.Event()

    def analyze(_workspace_id):
        release.wait(1)

    manager = AnalysisExecutionManager(analyze, max_workers=2)
    first = manager.submit("workspace-a")
    with pytest.raises(ExecutionConflictError):
        manager.submit("workspace-a")
    with pytest.raises(ExecutionTimeoutError):
        manager.wait(first.execution_id, timeout=0.001)
    running = manager.get(first.execution_id)
    assert running.state == ExecutionState.RUNNING
    assert running.phase == "analysis"
    assert running.progress_percent == 10
    release.set()
    completed = manager.wait(first.execution_id, timeout=1)

    assert completed.state == ExecutionState.COMPLETED
    assert completed.started_at is not None
    assert completed.finished_at is not None
    manager.shutdown()


def test_different_workspaces_can_execute_concurrently():
    barrier = threading.Barrier(2)
    observed = []

    def analyze(workspace_id):
        observed.append(workspace_id)
        barrier.wait(timeout=1)

    manager = AnalysisExecutionManager(analyze, max_workers=2)
    first = manager.submit("workspace-a")
    second = manager.submit("workspace-b")

    assert manager.wait(first.execution_id, 1).state == ExecutionState.COMPLETED
    assert manager.wait(second.execution_id, 1).state == ExecutionState.COMPLETED
    assert set(observed) == {"workspace-a", "workspace-b"}
    manager.shutdown()


def test_queued_execution_can_be_cancelled_without_running():
    release = threading.Event()
    observed = []

    def analyze(workspace_id):
        observed.append(workspace_id)
        if workspace_id == "workspace-a":
            release.wait(1)

    manager = AnalysisExecutionManager(analyze, max_workers=1)
    first = manager.submit("workspace-a")
    second = manager.submit("workspace-b")

    assert manager.cancel(second.execution_id) is True
    assert manager.get(second.execution_id).state == ExecutionState.CANCELLED
    release.set()
    manager.wait(first.execution_id, 1)
    assert observed == ["workspace-a"]
    manager.shutdown()


def test_failed_execution_is_sanitized_and_releases_workspace():
    def analyze(_workspace_id):
        raise ValueError("invalid project")

    manager = AnalysisExecutionManager(analyze)
    first = manager.submit("workspace")
    failed = manager.wait(first.execution_id, 1)
    second = manager.submit("workspace")

    assert failed.state == ExecutionState.FAILED
    assert failed.error == "Analysis failed"
    assert failed.error_category == "ValueError"
    assert failed.phase == "failed"
    assert failed.progress_percent == 100
    assert second.execution_id != first.execution_id
    manager.wait(second.execution_id, 1)
    manager.shutdown()
