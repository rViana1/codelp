from app.mcp.server import MCPServer, MCPServerState


def test_server_starts_in_created_state():
    server = MCPServer()

    assert server.state == MCPServerState.CREATED


def test_server_initialization_changes_state():
    server = MCPServer()

    server.initialize()

    assert server.state == MCPServerState.RUNNING


def test_server_shutdown_changes_state():
    server = MCPServer()

    server.initialize()
    server.shutdown()

    assert server.state == MCPServerState.STOPPED


def test_server_initialization_is_idempotent():
    server = MCPServer()

    server.initialize()
    server.initialize()

    assert server.state == MCPServerState.RUNNING
