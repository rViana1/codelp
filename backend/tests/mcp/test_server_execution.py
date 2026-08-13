from app.mcp.server import MCPServer


class DummyTool:

    name = "dummy"

    def execute(
        self,
        value,
    ):
        return {
            "value": value,
        }


def test_server_executes_registered_tool():

    server = MCPServer()

    server.register_tool_implementation(
        DummyTool()
    )

    result = server.execute_tool(
        "dummy",
        "hello",
    )

    assert result == {
        "value": "hello",
    }


def test_server_returns_none_for_unknown_tool():

    server = MCPServer()

    result = server.execute_tool(
        "unknown",
    )

    assert result is None
