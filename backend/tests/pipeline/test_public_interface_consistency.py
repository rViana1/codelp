import json

from typer.testing import CliRunner

from app.cli.main import cli
from app.api import create_rest_api
from app.configuration import CodelpSettings
from app.mcp.transport import CodelpMCPTransport
from app.runtime import create_codelp_application
from tests.api.test_rest_api import call


def mcp_request(server, request_id, method, params=None):
    payload = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        payload["params"] = params
    return server.handle(payload)


def test_cli_and_mcp_report_consistent_project_analysis(tmp_path):
    root = tmp_path / "demo"
    root.mkdir()
    (root / "main.py").write_text("def hello(): pass\n", encoding="utf-8")

    cli_result = CliRunner().invoke(cli, ["analyze", str(root), "--json"])
    cli_status = json.loads(cli_result.stdout)

    runtime = create_codelp_application(
        tmp_path / "mcp-knowledge",
        allowed_roots=(tmp_path,),
        settings=CodelpSettings(),
    )
    server = CodelpMCPTransport(runtime)
    opened = mcp_request(
        server,
        1,
        "tools/call",
        {"name": "workspace_open", "arguments": {"path": str(root)}},
    )
    workspace_id = opened["result"]["structuredContent"]["workspace_id"]
    analyzed = mcp_request(
        server,
        2,
        "tools/call",
        {
            "name": "workspace_analyze",
            "arguments": {"workspace_id": workspace_id},
        },
    )["result"]["structuredContent"]

    api_runtime = create_codelp_application(
        tmp_path / "api-knowledge",
        allowed_roots=(tmp_path,),
        settings=CodelpSettings(),
    )
    rest = create_rest_api(api_runtime)
    _, api_opened = call(
        rest, "POST", "/workspaces", {"path": str(root)}
    )
    _, api_status = call(
        rest,
        "POST",
        f"/workspaces/{api_opened['workspace_id']}/analyze",
    )

    assert cli_result.exit_code == 0
    assert analyzed["workspace_id"] == cli_status["workspace_id"]
    assert analyzed["files"] == cli_status["files"] == 1
    assert analyzed["symbols"] == cli_status["symbols"] == 1
    assert analyzed["graph_entities"] == cli_status["graph_entities"]
    assert analyzed["capabilities"] == cli_status["capabilities"]
    assert api_status["workspace_id"] == cli_status["workspace_id"]
    assert api_status["files"] == cli_status["files"]
    assert api_status["symbols"] == cli_status["symbols"]
    assert api_status["graph_entities"] == cli_status["graph_entities"]
    assert api_status["capabilities"] == cli_status["capabilities"]


def test_cli_mcp_and_rest_return_identical_query_and_exploration_results(
    tmp_path,
):
    root = tmp_path / "demo"
    root.mkdir()
    (root / "main.py").write_text(
        "def hello(name): return f'hello {name}'\n", encoding="utf-8"
    )
    cli_query = CliRunner().invoke(
        cli,
        ["query", "hello", "--path", str(root), "--json"],
    )
    cli_dependencies = CliRunner().invoke(
        cli,
        ["explore", "dependencies", "--path", str(root), "--json"],
    )

    settings = CodelpSettings(
        embeddings={"enabled": True, "provider": "local_hash"}
    )
    mcp_runtime = create_codelp_application(
        tmp_path / "mcp-query-knowledge",
        allowed_roots=(tmp_path,),
        settings=settings,
    )
    server = CodelpMCPTransport(mcp_runtime)
    opened = mcp_request(
        server,
        1,
        "tools/call",
        {"name": "workspace_open", "arguments": {"path": str(root)}},
    )
    workspace_id = opened["result"]["structuredContent"]["workspace_id"]
    mcp_request(
        server,
        2,
        "tools/call",
        {"name": "workspace_analyze", "arguments": {"workspace_id": workspace_id}},
    )
    mcp_query = mcp_request(
        server,
        3,
        "tools/call",
        {
            "name": "project_query",
            "arguments": {"workspace_id": workspace_id, "text": "hello"},
        },
    )["result"]["structuredContent"]
    mcp_dependencies = mcp_request(
        server,
        4,
        "tools/call",
        {
            "name": "project_explore",
            "arguments": {
                "workspace_id": workspace_id,
                "view": "dependencies",
            },
        },
    )["result"]["structuredContent"]

    api_runtime = create_codelp_application(
        tmp_path / "api-query-knowledge",
        allowed_roots=(tmp_path,),
        settings=settings,
    )
    rest = create_rest_api(api_runtime)
    _, api_opened = call(rest, "POST", "/workspaces", {"path": str(root)})
    api_workspace_id = api_opened["workspace_id"]
    call(rest, "POST", f"/workspaces/{api_workspace_id}/analyze")
    _, api_query = call(
        rest,
        "POST",
        f"/workspaces/{api_workspace_id}/query",
        {"text": "hello", "limit": 5},
    )
    _, api_dependencies = call(
        rest,
        "GET",
        f"/workspaces/{api_workspace_id}/dependencies",
    )

    assert cli_query.exit_code == cli_dependencies.exit_code == 0
    assert json.loads(cli_query.stdout) == mcp_query == api_query
    assert json.loads(cli_dependencies.stdout) == (
        mcp_dependencies["data"]
    ) == api_dependencies


def test_public_interfaces_map_invalid_targets_without_internal_details(tmp_path):
    missing = tmp_path / "missing"
    cli_result = CliRunner().invoke(cli, ["analyze", str(missing)])
    runtime = create_codelp_application(
        tmp_path / "knowledge", allowed_roots=(tmp_path,)
    )
    mcp_error = mcp_request(
        CodelpMCPTransport(runtime),
        1,
        "tools/call",
        {
            "name": "workspace_analyze",
            "arguments": {"workspace_id": "missing"},
        },
    )["error"]
    rest = create_rest_api(runtime)
    rest_status, rest_error = call(rest, "GET", "/workspaces/missing")

    assert cli_result.exit_code == 2
    assert "project_error" in cli_result.stderr
    assert mcp_error["data"]["category"] == "project_error"
    assert rest_status == 404
    assert rest_error["category"] == "project_error"
    assert "Traceback" not in cli_result.stderr
