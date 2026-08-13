from app.mcp.bootstrap import create_mcp_server


def test_server_returns_none_for_unknown_resource():

    server = create_mcp_server()

    resource = server._resources.get(
        "project://unknown"
    )

    assert resource is None
