import io
import json

from app.configuration import CodelpSettings
from app.mcp.transport import CodelpMCPTransport
from app.runtime import create_codelp_application


def transport(tmp_path):
    application = create_codelp_application(
        tmp_path / "knowledge",
        settings=CodelpSettings(
            embeddings={"enabled": True, "provider": "local_hash"}
        ),
    )
    return CodelpMCPTransport(application)


def request(transport, request_id, method, params=None):
    payload = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        payload["params"] = params
    return transport.handle(payload)


def test_current_discovery_and_legacy_initialize_are_supported(tmp_path):
    server = transport(tmp_path)

    current = request(server, 1, "server/discover")
    legacy = request(
        server,
        2,
        "initialize",
        {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1"},
        },
    )

    assert current["result"]["protocolVersion"] == "2026-07-28"
    assert legacy["result"]["protocolVersion"] == "2025-11-25"
    assert current["result"]["capabilities"] == {
        "tools": {"listChanged": False},
        "resources": {"subscribe": False, "listChanged": True},
    }


def test_mcp_tools_open_analyze_explore_query_and_close_workspace(tmp_path):
    root = tmp_path / "demo"
    root.mkdir()
    (root / "main.py").write_text(
        "def hello():\n    return 'hello'\n", encoding="utf-8"
    )
    server = transport(tmp_path)

    tools = request(server, 1, "tools/list")["result"]["tools"]
    assert [item["name"] for item in tools] == [
        "workspace_open",
        "workspace_analyze",
        "project_explore",
        "project_query",
        "workspace_close",
    ]
    opened = request(
        server,
        2,
        "tools/call",
        {"name": "workspace_open", "arguments": {"path": str(root)}},
    )
    workspace_id = opened["result"]["structuredContent"]["workspace_id"]
    analyzed = request(
        server,
        3,
        "tools/call",
        {
            "name": "workspace_analyze",
            "arguments": {"workspace_id": workspace_id},
        },
    )
    explored = request(
        server,
        4,
        "tools/call",
        {
            "name": "project_explore",
            "arguments": {
                "workspace_id": workspace_id,
                "view": "project",
            },
        },
    )
    queried = request(
        server,
        5,
        "tools/call",
        {
            "name": "project_query",
            "arguments": {"workspace_id": workspace_id, "text": "hello"},
        },
    )

    assert analyzed["result"]["structuredContent"]["state"] == "analyzed"
    assert explored["result"]["structuredContent"]["project_id"] == "demo"
    assert queried["result"]["structuredContent"]["results"]

    closed = request(
        server,
        6,
        "tools/call",
        {
            "name": "workspace_close",
            "arguments": {"workspace_id": workspace_id},
        },
    )
    assert closed["result"]["structuredContent"]["state"] == "closed"


def test_mcp_resources_are_dynamic_and_readable(tmp_path):
    root = tmp_path / "demo"
    root.mkdir()
    (root / "main.py").write_text("def hello(): pass\n", encoding="utf-8")
    server = transport(tmp_path)
    opened = request(
        server,
        1,
        "tools/call",
        {"name": "workspace_open", "arguments": {"path": str(root)}},
    )
    workspace_id = opened["result"]["structuredContent"]["workspace_id"]
    request(
        server,
        2,
        "tools/call",
        {
            "name": "workspace_analyze",
            "arguments": {"workspace_id": workspace_id},
        },
    )

    resources = request(server, 3, "resources/list")["result"]["resources"]
    uri = f"codelp://workspace/{workspace_id}/knowledge"
    assert uri in {item["uri"] for item in resources}
    read = request(server, 4, "resources/read", {"uri": uri})
    content = json.loads(read["result"]["contents"][0]["text"])
    assert content["project_id"] == "demo"


def test_stdio_transport_returns_parse_and_method_errors(tmp_path):
    source = io.StringIO(
        "not-json\n"
        + json.dumps(
            {"jsonrpc": "2.0", "id": 2, "method": "unknown"}
        )
        + "\n"
    )
    output = io.StringIO()

    transport(tmp_path).run_stdio(source, output)

    responses = [json.loads(line) for line in output.getvalue().splitlines()]
    assert responses[0]["error"]["code"] == -32700
    assert responses[1]["error"]["code"] == -32601


def test_tool_argument_validation_returns_protocol_error(tmp_path):
    missing = request(
        transport(tmp_path),
        1,
        "tools/call",
        {"name": "workspace_open", "arguments": {}},
    )

    assert missing["error"] == {
        "code": -32602,
        "message": "Missing tool arguments: path",
    }


def test_mcp_authorization_boundary_is_injected(tmp_path):
    server = transport(tmp_path)
    server.authorize = lambda payload: payload.get("params", {}).get("token") == "ok"

    denied = request(server, 1, "tools/list")

    assert denied["error"] == {
        "code": -32001,
        "message": "Request is not authorized",
    }
