from app.mcp.models import (
    MCPRetrievalResponse,
)


def test_retrieval_response_serializes_deterministically():

    response = MCPRetrievalResponse(
        query="authentication",
        results=[],
    )

    assert response.model_dump() == {
        "query": "authentication",
        "results": [],
    }
