"""Thread-safe project analysis execution management."""

from __future__ import annotations

import hashlib
import threading
from concurrent.futures import Future, ThreadPoolExecutor, TimeoutError
from datetime import datetime, timezone
from enum import Enum
from typing import Callable

from pydantic import BaseModel


class ExecutionState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AnalysisExecution(BaseModel):
    execution_id: str
    workspace_id: str
    state: ExecutionState
    submitted_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error: str | None = None


class ExecutionConflictError(RuntimeError):
    pass


class ExecutionTimeoutError(TimeoutError):
    pass


class AnalysisExecutionManager:
    """Run one analysis per workspace while allowing different projects."""

    def __init__(
        self,
        analyze: Callable[[str], object],
        *,
        max_workers: int = 4,
    ) -> None:
        self._analyze = analyze
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="codelp-analysis",
        )
        self._guard = threading.RLock()
        self._records: dict[str, AnalysisExecution] = {}
        self._futures: dict[str, Future] = {}
        self._active_by_workspace: dict[str, str] = {}
        self._sequence = 0

    def submit(self, workspace_id: str) -> AnalysisExecution:
        with self._guard:
            active = self._active_by_workspace.get(workspace_id)
            if active is not None:
                raise ExecutionConflictError(
                    f"Workspace analysis already active: {active}"
                )
            self._sequence += 1
            execution_id = hashlib.sha256(
                f"{workspace_id}:{self._sequence}".encode("utf-8")
            ).hexdigest()
            record = AnalysisExecution(
                execution_id=execution_id,
                workspace_id=workspace_id,
                state=ExecutionState.QUEUED,
                submitted_at=datetime.now(timezone.utc),
            )
            self._records[execution_id] = record
            self._active_by_workspace[workspace_id] = execution_id
            self._futures[execution_id] = self._executor.submit(
                self._run, execution_id
            )
            return record.model_copy(deep=True)

    def _run(self, execution_id: str) -> None:
        with self._guard:
            record = self._records[execution_id]
            if record.state == ExecutionState.CANCELLED:
                return
            record.state = ExecutionState.RUNNING
            record.started_at = datetime.now(timezone.utc)
        try:
            self._analyze(record.workspace_id)
        except Exception as exc:
            with self._guard:
                record.state = ExecutionState.FAILED
                record.error = type(exc).__name__
        else:
            with self._guard:
                record.state = ExecutionState.COMPLETED
        finally:
            with self._guard:
                record.finished_at = datetime.now(timezone.utc)
                self._active_by_workspace.pop(record.workspace_id, None)

    def get(self, execution_id: str) -> AnalysisExecution:
        with self._guard:
            record = self._records.get(execution_id)
            if record is None:
                raise KeyError(execution_id)
            return record.model_copy(deep=True)

    def list(self) -> tuple[AnalysisExecution, ...]:
        with self._guard:
            return tuple(
                self._records[key].model_copy(deep=True)
                for key in sorted(self._records)
            )

    def cancel(self, execution_id: str) -> bool:
        with self._guard:
            record = self._records.get(execution_id)
            if record is None:
                raise KeyError(execution_id)
            if record.state != ExecutionState.QUEUED:
                return False
            future = self._futures[execution_id]
            if not future.cancel():
                return False
            record.state = ExecutionState.CANCELLED
            record.finished_at = datetime.now(timezone.utc)
            self._active_by_workspace.pop(record.workspace_id, None)
            return True

    def wait(
        self, execution_id: str, timeout: float | None = None
    ) -> AnalysisExecution:
        future = self._futures.get(execution_id)
        if future is None:
            raise KeyError(execution_id)
        try:
            future.result(timeout=timeout)
        except TimeoutError as exc:
            raise ExecutionTimeoutError(execution_id) from exc
        return self.get(execution_id)

    def is_workspace_active(self, workspace_id: str) -> bool:
        with self._guard:
            return workspace_id in self._active_by_workspace

    def shutdown(self, wait: bool = True) -> None:
        self._executor.shutdown(wait=wait, cancel_futures=not wait)
