from pathlib import Path

from app.mcp.models import (
    MCPResponse,
    MCPToolResponse,
)


def test_mcp_responses_are_external_contracts():

    response = MCPResponse(
        result={
            "name": "test-project",
            "root_path": "/tmp/project",
        }
    )

    data = response.model_dump()

    assert data["result"]["name"] == "test-project"
    assert data["error"] is None


def test_mcp_tool_response_has_stable_contract():

    response = MCPToolResponse(
        success=True,
        data={
            "symbol": "User.login",
        },
    )

    data = response.model_dump()

    assert data["success"] is True
    assert data["data"]["symbol"] == "User.login"
    assert data["diagnostics"] == []


def test_mcp_does_not_expose_python_file_objects():

    response = MCPResponse(
        result={
            "path": "/tmp/project/main.py",
        }
    )

    serialized = response.model_dump_json()

    assert isinstance(serialized, str)
    assert "main.py" in serialized
