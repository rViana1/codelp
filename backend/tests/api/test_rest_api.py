import asyncio
import json

from app.api import create_rest_api
from app.configuration import CodelpSettings
from app.runtime import create_codelp_application


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


def call(application, method, path, body=None, query_string=""):
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

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": query_string.encode(),
        "headers": [(b"content-type", b"application/json")],
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
    assert missing_status == 404
    assert missing["code"] == "workspace_not_found"


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
