"""FastAPI transport over the transport-neutral Codelp runtime."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from app.runtime import CodelpApplication
from app.runtime.exceptions import WorkspaceNotFoundError
from app.runtime.security import WorkspaceSecurityError

from .models import QueryRequest, WorkspaceOpenRequest, WorkspaceResponse


def create_rest_api(
    application: CodelpApplication,
    *,
    authorize: Callable[[Request], bool] | None = None,
) -> FastAPI:
    api = FastAPI(
        title="Codelp API",
        version="0.11.0",
        description="Deterministic project knowledge without an LLM requirement.",
    )

    @api.middleware("http")
    async def authorization_boundary(request: Request, call_next):
        if authorize is not None and request.url.path not in {"/health", "/ready"}:
            if not authorize(request):
                return JSONResponse(
                    status_code=401,
                    content={
                        "code": "unauthorized",
                        "message": "Request is not authorized",
                    },
                )
        return await call_next(request)

    @api.exception_handler(WorkspaceNotFoundError)
    async def workspace_not_found(_request, exc):
        return JSONResponse(
            status_code=404,
            content={
                "code": "workspace_not_found",
                "message": f"Unknown workspace: {exc.args[0]}",
            },
        )

    @api.exception_handler(RuntimeError)
    async def capability_unavailable(_request, exc):
        return JSONResponse(
            status_code=409,
            content={"code": "capability_unavailable", "message": str(exc)},
        )

    @api.exception_handler(WorkspaceSecurityError)
    async def workspace_forbidden(_request, exc):
        return JSONResponse(
            status_code=403,
            content={"code": "workspace_forbidden", "message": str(exc)},
        )

    @api.get("/health")
    async def health():
        return {"status": "ok", "service": "codelp"}

    @api.get("/ready")
    async def ready():
        return {"status": "ready"}

    @api.get("/metrics")
    async def metrics():
        return application.observability.metrics()

    @api.post(
        "/workspaces",
        response_model=WorkspaceResponse,
        status_code=201,
    )
    async def open_workspace(payload: WorkspaceOpenRequest):
        try:
            workspace = application.open_project(
                payload.path,
                name=payload.name,
            )
        except (FileNotFoundError, NotADirectoryError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return WorkspaceResponse(
            workspace_id=workspace.workspace_id,
            state=workspace.state.value,
        )

    @api.get("/workspaces")
    async def list_workspaces():
        return [
            item.model_dump(mode="json")
            for item in application.list_workspaces()
        ]

    @api.post("/workspaces/{workspace_id}/analyze")
    async def analyze_workspace(workspace_id: str):
        application.analyze(workspace_id)
        return application.status(workspace_id).model_dump(mode="json")

    @api.post("/workspaces/{workspace_id}/executions", status_code=202)
    async def submit_execution(workspace_id: str):
        return application.submit_analysis(workspace_id).model_dump(mode="json")

    @api.get("/executions/{execution_id}")
    async def execution_status(execution_id: str):
        try:
            return application.execution_status(execution_id).model_dump(
                mode="json"
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Execution not found") from exc

    @api.delete("/executions/{execution_id}")
    async def cancel_execution(execution_id: str):
        try:
            cancelled = application.cancel_execution(execution_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Execution not found") from exc
        if not cancelled:
            raise HTTPException(
                status_code=409,
                detail="Only queued executions can be cancelled safely",
            )
        return {"execution_id": execution_id, "state": "cancelled"}

    @api.get("/workspaces/{workspace_id}")
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

    @api.get("/workspaces/{workspace_id}/context")
    async def workspace_context(workspace_id: str):
        return application.explore(workspace_id, "context")

    @api.get("/workspaces/{workspace_id}/knowledge")
    async def workspace_knowledge(workspace_id: str):
        return application.explore(workspace_id, "project")

    @api.get("/workspaces/{workspace_id}/symbols/{symbol_id:path}")
    async def workspace_symbol(workspace_id: str, symbol_id: str):
        result = application.explore(workspace_id, "symbol", symbol_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Symbol not found")
        return result

    @api.get("/workspaces/{workspace_id}/explore/{view}")
    async def explore_workspace(
        workspace_id: str,
        view: str,
        entity_id: str | None = Query(default=None),
    ):
        try:
            return application.explore(workspace_id, view, entity_id)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    return api
