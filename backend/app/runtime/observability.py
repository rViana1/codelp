"""Structured, content-safe runtime events and metrics."""

from __future__ import annotations

import hashlib
import json
import logging
import threading
from collections import Counter
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class RuntimeEvent(BaseModel):
    correlation_id: str
    operation: str
    status: str
    workspace_id: str | None = None
    timestamp: datetime
    duration_seconds: float | None = None
    metrics: dict[str, int | float | str | bool] = Field(default_factory=dict)
    error_category: str | None = None


class RuntimeObservability:
    """Record safe operational facts without source text or secret values."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger("codelp.runtime")
        self._events: list[RuntimeEvent] = []
        self._counters: Counter[str] = Counter()
        self._sequence = 0
        self._lock = threading.RLock()

    def correlation_id(
        self, operation: str, workspace_id: str | None
    ) -> str:
        with self._lock:
            self._sequence += 1
            return hashlib.sha256(
                f"{operation}:{workspace_id or '-'}:{self._sequence}".encode()
            ).hexdigest()

    def record(
        self,
        *,
        correlation_id: str,
        operation: str,
        status: str,
        workspace_id: str | None = None,
        duration_seconds: float | None = None,
        metrics: dict[str, int | float | str | bool] | None = None,
        error_category: str | None = None,
    ) -> RuntimeEvent:
        event = RuntimeEvent(
            correlation_id=correlation_id,
            operation=operation,
            status=status,
            workspace_id=workspace_id,
            timestamp=datetime.now(timezone.utc),
            duration_seconds=duration_seconds,
            metrics=metrics or {},
            error_category=error_category,
        )
        with self._lock:
            self._events.append(event)
            self._counters[f"{operation}.{status}"] += 1
        self.logger.info(
            json.dumps(event.model_dump(mode="json"), sort_keys=True)
        )
        return event

    def events(self) -> tuple[RuntimeEvent, ...]:
        with self._lock:
            return tuple(item.model_copy(deep=True) for item in self._events)

    def metrics(self) -> dict[str, int]:
        with self._lock:
            return dict(sorted(self._counters.items()))
