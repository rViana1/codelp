class MCPToolExecutor:
    """
    Executes MCP tools through registered implementations.

    This class separates MCP contracts from
    application execution.
    """

    def __init__(self) -> None:
        self._tools: dict[str, object] = {}

    def register(
        self,
        tool: object,
    ) -> None:
        self._tools[tool.name] = tool

    def execute(
        self,
        name: str,
        *args,
        **kwargs,
    ):
        tool = self._tools.get(name)

        if tool is None:
            return None

        return tool.execute(
            *args,
            **kwargs,
        )
