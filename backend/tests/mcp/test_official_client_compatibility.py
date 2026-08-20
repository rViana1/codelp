from pathlib import Path

import anyio
from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client


def test_official_mcp_client_negotiates_and_lists_codelp_tools(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    (root / "main.py").write_text("def hello(): return 'hello'\n")
    executable = Path(__file__).resolve().parents[3] / ".venv/bin/codelp-mcp"

    async def exercise_client():
        parameters = StdioServerParameters(
            command=str(executable),
            args=[],
            cwd=root,
        )
        async with Client(stdio_client(parameters)) as client:
            tools = await client.list_tools()
            assert client.protocol_version in {"2026-07-28", "2025-11-25"}
            assert {tool.name for tool in tools.tools} >= {
                "workspace_open",
                "workspace_analyze",
                "project_explore",
                "project_query",
                "project_context",
                "workspace_close",
            }
            opened = await client.call_tool(
                "workspace_open", {"path": str(root)}
            )
            assert opened.is_error is False
            assert opened.structured_content["workspace_id"]

    anyio.run(exercise_client)
