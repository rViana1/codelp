from app.mcp.models import (
    MCPProjectInformation,
    MCPToolRequest,
    MCPToolResponse,
)


def test_project_information_model_serializes_deterministically():
    model = MCPProjectInformation(
        name="test-project",
        root_path="/tmp/test-project",
        statistics={
            "scanned_files": [
                "src/main.py",
                "README.md",
            ]
        },
    )

    assert model.model_dump() == {
        "name": "test-project",
        "root_path": "/tmp/test-project",
        "statistics": {
            "scanned_files": [
                "src/main.py",
                "README.md",
            ]
        },
    }


def test_tool_request_defaults_parameters():
    request = MCPToolRequest()

    assert request.parameters == {}


def test_tool_response_defaults_are_deterministic():
    response = MCPToolResponse(
        success=True,
    )

    assert response.model_dump() == {
        "success": True,
        "data": {},
        "diagnostics": [],
    }


def test_tool_response_accepts_data_and_diagnostics():
    response = MCPToolResponse(
        success=False,
        data={
            "error": "project_not_found",
        },
        diagnostics=[
            "Missing project knowledge",
        ],
    )

    assert response.data["error"] == "project_not_found"
    assert response.diagnostics == [
        "Missing project knowledge",
    ]
