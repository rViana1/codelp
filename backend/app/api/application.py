"""FastAPI transport over the transport-neutral Codelp runtime."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.runtime import (
    CodelpApplication,
    DiagnosticCategory,
    categorize_exception,
    safe_diagnostic_message,
)
from app.runtime.exceptions import InterfaceDisabledError

from .models import (
    ExecutionResponse,
    QueryRequest,
    WorkspaceOpenRequest,
    WorkspaceResponse,
    WorkspaceStatusResponse,
)


def _error(status: int, code: str, message: str, category: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"code": code, "message": message, "category": category},
    )


def _status_for(category: DiagnosticCategory) -> int:
    return {
        DiagnosticCategory.USER: 400,
        DiagnosticCategory.PROJECT: 404,
        DiagnosticCategory.CONFIGURATION: 400,
        DiagnosticCategory.CAPABILITY: 409,
        DiagnosticCategory.SECURITY: 403,
        DiagnosticCategory.CONFLICT: 409,
        DiagnosticCategory.TIMEOUT: 408,
        DiagnosticCategory.INTERNAL: 500,
    }[category]


def create_rest_api(
    application: CodelpApplication,
    *,
    authorize: Callable[[Request], bool] | None = None,
) -> FastAPI:
    if not application.settings.interfaces.rest_enabled:
        raise InterfaceDisabledError("rest")
    @asynccontextmanager
    async def lifespan(_api):
        yield
        application.shutdown()

    api = FastAPI(
        title="Codelp API",
        version="0.11.0",
        description="Deterministic project knowledge without an LLM requirement.",
        lifespan=lifespan,
    )

    @api.middleware("http")
    async def operational_boundary(request: Request, call_next):
        content_length = request.headers.get("content-length")
        try:
            request_size = int(content_length) if content_length is not None else 0
        except ValueError:
            return _error(
                400,
                "invalid_content_length",
                "Content-Length must be an integer",
                DiagnosticCategory.USER.value,
            )
        if request_size > application.settings.security.max_request_bytes:
            return _error(
                413,
                "request_too_large",
                "Request exceeds configured size limit",
                DiagnosticCategory.SECURITY.value,
            )
        if authorize is not None and request.url.path not in {"/health", "/ready"}:
            if not authorize(request):
                return _error(
                    401,
                    "unauthorized",
                    "Request is not authorized",
                    DiagnosticCategory.SECURITY.value,
                )
        return await call_next(request)

    @api.exception_handler(RequestValidationError)
    async def request_validation_error(_request, _exc):
        return _error(
            422,
            "validation_error",
            "Request does not match the public API contract",
            DiagnosticCategory.USER.value,
        )

    @api.exception_handler(HTTPException)
    async def http_error(_request, exc):
        detail = exc.detail
        if isinstance(detail, dict):
            code = str(detail.get("code", "request_error"))
            message = str(detail.get("message", "Request failed"))
            category = str(
                detail.get("category", DiagnosticCategory.USER.value)
            )
        else:
            code = "request_error"
            message = str(detail)
            category = DiagnosticCategory.USER.value
        return _error(exc.status_code, code, message, category)

    @api.exception_handler(RuntimeError)
    @api.exception_handler(FileNotFoundError)
    @api.exception_handler(NotADirectoryError)
    @api.exception_handler(PermissionError)
    @api.exception_handler(ValueError)
    @api.exception_handler(KeyError)
    @api.exception_handler(TimeoutError)
    @api.exception_handler(Exception)
    async def application_error(_request, exc):
        category = categorize_exception(exc)
        code = (
            "workspace_not_found"
            if exc.__class__.__name__ == "WorkspaceNotFoundError"
            else category.value
        )
        return _error(
            _status_for(category),
            code,
            safe_diagnostic_message(exc),
            category.value,
        )

    @api.get("/")
    async def service_document():
        return {
            "service": "codelp",
            "version": "0.11.0",
            "documentation": "/docs",
            "health": "/health",
        }

    @api.get("/health")
    async def health():
        return {"status": "ok", "service": "codelp"}

    @api.get("/ready")
    async def ready():
        return {"status": "ready"}

    @api.get("/metrics")
    async def metrics():
        return application.observability.metrics()

    @api.post("/workspaces", response_model=WorkspaceResponse, status_code=201)
    async def open_workspace(payload: WorkspaceOpenRequest):
        workspace = application.open_project(payload.path, name=payload.name)
        return WorkspaceResponse(
            workspace_id=workspace.workspace_id,
            state=workspace.state.value,
        )

    @api.get("/workspaces", response_model=list[WorkspaceStatusResponse])
    async def list_workspaces():
        return [
            item.model_dump(mode="json")
            for item in application.list_workspaces()
        ]

    @api.post(
        "/workspaces/{workspace_id}/analyze",
        response_model=WorkspaceStatusResponse,
    )
    async def analyze_workspace(workspace_id: str):
        application.analyze(workspace_id)
        return application.status(workspace_id).model_dump(mode="json")

    @api.post(
        "/workspaces/{workspace_id}/executions",
        status_code=202,
        response_model=ExecutionResponse,
    )
    async def submit_execution(workspace_id: str):
        return application.submit_analysis(workspace_id).model_dump(mode="json")

    @api.get(
        "/executions/{execution_id}", response_model=ExecutionResponse
    )
    async def execution_status(execution_id: str):
        try:
            result = application.execution_status(execution_id)
        except KeyError as exc:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "execution_not_found",
                    "message": "Execution not found",
                    "category": DiagnosticCategory.PROJECT.value,
                },
            ) from exc
        return result.model_dump(mode="json")

    @api.get(
        "/executions/{execution_id}/wait", response_model=ExecutionResponse
    )
    async def wait_execution(
        execution_id: str,
        timeout: float | None = Query(default=None, gt=0, le=300),
    ):
        try:
            result = application.wait_for_execution(
                execution_id,
                timeout or application.settings.execution.default_wait_timeout_seconds,
            )
        except KeyError as exc:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "execution_not_found",
                    "message": "Execution not found",
                    "category": DiagnosticCategory.PROJECT.value,
                },
            ) from exc
        return result.model_dump(mode="json")

    @api.delete("/executions/{execution_id}")
    async def cancel_execution(execution_id: str):
        try:
            cancelled = application.cancel_execution(execution_id)
        except KeyError as exc:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "execution_not_found",
                    "message": "Execution not found",
                    "category": DiagnosticCategory.PROJECT.value,
                },
            ) from exc
        if not cancelled:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "execution_conflict",
                    "message": "Only queued executions can be cancelled safely",
                    "category": DiagnosticCategory.CONFLICT.value,
                },
            )
        return {"execution_id": execution_id, "state": "cancelled"}

    @api.get(
        "/workspaces/{workspace_id}", response_model=WorkspaceStatusResponse
    )
    async def workspace_status(workspace_id: str):
        return application.status(workspace_id).model_dump(mode="json")

    @api.delete("/workspaces/{workspace_id}")
    async def close_workspace(workspace_id: str):
        workspace = application.close_project(workspace_id)
        return {"workspace_id": workspace.workspace_id, "state": "closed"}

    @api.post("/workspaces/{workspace_id}/query")
    async def query_workspace(workspace_id: str, payload: QueryRequest):
        return application.query(
            workspace_id,
            payload.text,
            limit=payload.limit,
        ).model_dump(mode="json")

    @api.post("/workspaces/{workspace_id}/context")
    async def generate_context(workspace_id: str, payload: QueryRequest):
        application.query(workspace_id, payload.text, limit=payload.limit)
        return application.explore(workspace_id, "context")

    @api.get("/workspaces/{workspace_id}/context")
    async def workspace_context(workspace_id: str):
        return application.explore(workspace_id, "context")

    @api.get("/workspaces/{workspace_id}/knowledge")
    async def workspace_knowledge(workspace_id: str):
        return application.explore(workspace_id, "project")

    @api.get("/workspaces/{workspace_id}/understanding")
    async def workspace_understanding(workspace_id: str):
        result = application.understand(workspace_id)
        return result.model_dump(mode="json") if result is not None else None

    @api.get("/workspaces/{workspace_id}/symbols/{symbol_id:path}")
    async def workspace_symbol(workspace_id: str, symbol_id: str):
        result = application.explore(workspace_id, "symbol", symbol_id)
        if result is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "symbol_not_found",
                    "message": "Symbol not found",
                    "category": DiagnosticCategory.PROJECT.value,
                },
            )
        return result

    def relationship_view(workspace_id: str, view: str, entity_id: str | None):
        return application.explore(workspace_id, view, entity_id)

    @api.get("/workspaces/{workspace_id}/dependencies")
    async def dependencies(workspace_id: str, entity_id: str | None = None):
        return relationship_view(workspace_id, "dependencies", entity_id)

    @api.get("/workspaces/{workspace_id}/history")
    async def history(workspace_id: str, entity_id: str | None = None):
        return relationship_view(workspace_id, "history", entity_id)

    @api.get("/workspaces/{workspace_id}/duplicates")
    async def duplicates(workspace_id: str, entity_id: str | None = None):
        return relationship_view(workspace_id, "duplicates", entity_id)

    @api.get("/workspaces/{workspace_id}/similarity")
    async def similarity(workspace_id: str, entity_id: str | None = None):
        return relationship_view(workspace_id, "similarity", entity_id)

    @api.get("/workspaces/{workspace_id}/explore/{view}")
    async def explore_workspace(
        workspace_id: str,
        view: str,
        entity_id: str | None = Query(default=None),
    ):
        return application.explore(workspace_id, view, entity_id)

    return api
