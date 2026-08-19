from pathlib import Path


def test_protocol_transport_delegates_to_runtime_only():
    content = Path("backend/app/mcp/transport.py").read_text(encoding="utf-8")

    assert "app.runtime" in content
    assert "PipelineAnalyzer" not in content
    assert "KnowledgeStorage" not in content
    assert "PersistentProjectKnowledge" not in content
    assert "FileKnowledgeStorage" not in content
