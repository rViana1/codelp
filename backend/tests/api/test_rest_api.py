import asyncio
import json
import threading

import pytest

from app.api import create_rest_api
from app.configuration import CodelpSettings
from app.runtime import create_codelp_application
from app.runtime.exceptions import InterfaceDisabledError


def api(tmp_path, *, embeddings=True):
    runtime = create_codelp_application(
        tmp_path / "knowledge",
        settings=CodelpSettings(
            embeddings={
                "enabled": embeddings,
                "provider": "local_hash" if embeddings else "disabled",
            }
        ),
    )
    return create_rest_api(runtime)


def call(application, method, path, body=None, query_string="", headers=None):
    messages = []
    encoded = json.dumps(body).encode() if body is not None else b""
    received = False

    async def receive():
        nonlocal received
        if received:
            return {"type": "http.disconnect"}
        received = True
        return {"type": "http.request", "body": encoded, "more_body": False}

    async def send(message):
        messages.append(message)

    request_headers = [(b"content-type", b"application/json")]
    request_headers.extend(headers or [])
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": query_string.encode(),
        "headers": request_headers,
        "client": ("test", 1),
        "server": ("test", 80),
        "root_path": "",
    }
    asyncio.run(application(scope, receive, send))
    status = next(item["status"] for item in messages if item["type"] == "http.response.start")
    payload = b"".join(
        item.get("body", b"")
        for item in messages
        if item["type"] == "http.response.body"
    )
    return status, json.loads(payload or b"null")


def project(tmp_path):
    root = tmp_path / "demo"
    root.mkdir()
    (root / "main.py").write_text("def hello(): return 'hello'\n", encoding="utf-8")
    return root


def test_health_readiness_and_openapi_contract(tmp_path):
    application = api(tmp_path)

    assert call(application, "GET", "/health") == (
        200,
        {"status": "ok", "service": "codelp"},
    )
    assert call(application, "GET", "/ready") == (200, {"status": "ready"})
    schema = application.openapi()
    assert "/workspaces/{workspace_id}/query" in schema["paths"]
    assert "/workspaces/{workspace_id}/understanding" in schema["paths"]
    assert "/workspaces/{workspace_id}/dependencies" in schema["paths"]
    assert "/executions/{execution_id}/wait" in schema["paths"]


def test_workspace_analysis_query_and_exploration_api(tmp_path):
    application = api(tmp_path)
    opened_status, opened = call(
        application,
        "POST",
        "/workspaces",
        {"path": str(project(tmp_path))},
    )
    workspace_id = opened["workspace_id"]

    analyzed_status, analyzed = call(
        application, "POST", f"/workspaces/{workspace_id}/analyze"
    )
    query_status, query = call(
        application,
        "POST",
        f"/workspaces/{workspace_id}/query",
        {"text": "hello", "limit": 3},
    )
    knowledge_status, knowledge = call(
        application, "GET", f"/workspaces/{workspace_id}/knowledge"
    )

    assert opened_status == 201
    assert analyzed_status == query_status == knowledge_status == 200
    assert analyzed["state"] == "analyzed"
    assert query["results"]
    assert knowledge["project_id"] == "demo"


def test_api_maps_workspace_capability_and_validation_errors(tmp_path):
    application = api(tmp_path, embeddings=False)
    _, opened = call(
        application,
        "POST",
        "/workspaces",
        {"path": str(project(tmp_path))},
    )
    workspace_id = opened["workspace_id"]
    call(application, "POST", f"/workspaces/{workspace_id}/analyze")

    capability_status, capability = call(
        application,
        "POST",
        f"/workspaces/{workspace_id}/query",
        {"text": "hello"},
    )
    missing_status, missing = call(application, "GET", "/workspaces/missing")

    assert capability_status == 409
    assert capability["code"] == "capability_unavailable"
    assert capability["category"] == "capability_unavailable"
    assert missing_status == 404
    assert missing["code"] == "workspace_not_found"
    assert missing["category"] == "project_error"


def test_api_authorization_is_injected_and_does_not_store_credentials(tmp_path):
    runtime = create_codelp_application(
        tmp_path / "knowledge", allowed_roots=(tmp_path,)
    )
    application = create_rest_api(
        runtime,
        authorize=lambda request: request.headers.get("authorization") == "ok",
    )

    status, payload = call(application, "GET", "/workspaces")

    assert status == 401
    assert payload["code"] == "unauthorized"
    assert call(application, "GET", "/health")[0] == 200


def test_dedicated_understanding_relationship_and_context_endpoints(tmp_path):
    application = api(tmp_path)
    _, opened = call(
        application,
        "POST",
        "/workspaces",
        {"path": str(project(tmp_path))},
    )
    workspace_id = opened["workspace_id"]
    call(application, "POST", f"/workspaces/{workspace_id}/analyze")

    for suffix in (
        "understanding",
        "dependencies",
        "history",
        "duplicates",
        "similarity",
    ):
        status, _payload = call(
            application, "GET", f"/workspaces/{workspace_id}/{suffix}"
        )
        assert status == 200
    status, context = call(
        application,
        "POST",
        f"/workspaces/{workspace_id}/context",
        {"text": "hello", "limit": 3},
    )
    assert status == 200
    assert context["context"] is not None


def test_execution_progress_wait_and_uniform_validation_error(tmp_path):
    application = api(tmp_path)
    _, opened = call(
        application,
        "POST",
        "/workspaces",
        {"path": str(project(tmp_path))},
    )
    workspace_id = opened["workspace_id"]
    submitted_status, submitted = call(
        application,
        "POST",
        f"/workspaces/{workspace_id}/executions",
    )
    waited_status, waited = call(
        application,
        "GET",
        f"/executions/{submitted['execution_id']}/wait",
        query_string="timeout=2",
    )
    invalid_status, invalid = call(
        application,
        "POST",
        "/workspaces",
        {"path": str(tmp_path), "unexpected": True},
    )

    assert submitted_status == 202
    assert waited_status == 200
    assert waited["state"] == "completed"
    assert waited["phase"] == "completed"
    assert waited["progress_percent"] == 100
    assert invalid_status == 422
    assert invalid == {
        "code": "validation_error",
        "message": "Request does not match the public API contract",
        "category": "user_error",
    }


def test_rest_request_size_limit_is_enforced(tmp_path):
    runtime = create_codelp_application(
        tmp_path / "knowledge",
        allowed_roots=(tmp_path,),
        settings=CodelpSettings(security={"max_request_bytes": 4}),
    )
    application = create_rest_api(runtime)

    status, payload = call(
        application,
        "POST",
        "/workspaces",
        {"path": str(tmp_path)},
        headers=[(b"content-length", b"100")],
    )

    assert status == 413
    assert payload["code"] == "request_too_large"


def test_rest_wait_timeout_is_public_and_does_not_cancel_execution(tmp_path):
    release = threading.Event()
    runtime = create_codelp_application(
        tmp_path / "knowledge", allowed_roots=(tmp_path,)
    )
    runtime.execution_manager._analyze = lambda _workspace_id: release.wait(1)
    root = project(tmp_path)
    workspace = runtime.open_project(root)
    application = create_rest_api(runtime)
    _, submitted = call(
        application,
        "POST",
        f"/workspaces/{workspace.workspace_id}/executions",
    )

    status, payload = call(
        application,
        "GET",
        f"/executions/{submitted['execution_id']}/wait",
        query_string="timeout=0.001",
    )
    release.set()
    runtime.wait_for_execution(submitted["execution_id"], 1)

    assert status == 408
    assert payload["code"] == "execution_timeout"
    assert payload["category"] == "execution_timeout"


def test_rest_interface_toggle_is_enforced(tmp_path):
    runtime = create_codelp_application(
        tmp_path / "knowledge",
        allowed_roots=(tmp_path,),
        settings=CodelpSettings(interfaces={"rest_enabled": False}),
    )

    with pytest.raises(InterfaceDisabledError):
        create_rest_api(runtime)
