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
