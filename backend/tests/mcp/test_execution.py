from app.mcp.execution import MCPToolExecutor


class DummyTool:

    name = "dummy"

    def execute(
        self,
        value,
    ):
        return {
            "value": value,
        }


def test_executor_registers_and_executes_tool():

    executor = MCPToolExecutor()

    executor.register(
        DummyTool()
    )

    result = executor.execute(
        "dummy",
        "test",
    )

    assert result == {
        "value": "test",
    }


def test_executor_returns_none_for_unknown_tool():

    executor = MCPToolExecutor()

    result = executor.execute(
        "missing",
    )

    assert result is None
