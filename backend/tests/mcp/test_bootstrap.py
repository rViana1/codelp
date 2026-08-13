from app.mcp.bootstrap import create_mcp_server
from app.mcp.server import MCPServer


def test_create_mcp_server_returns_server():

    server = create_mcp_server()

    assert isinstance(
        server,
        MCPServer,
    )


def test_create_mcp_server_registers_resources_and_tools():

    server = create_mcp_server()

    assert len(server.tools()) > 0

    assert len(server.resources()) > 0
