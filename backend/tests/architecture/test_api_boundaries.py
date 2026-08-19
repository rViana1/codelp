from pathlib import Path


def test_rest_api_delegates_to_runtime_without_pipeline_or_storage_access():
    content = Path("backend/app/api/application.py").read_text(encoding="utf-8")

    assert "app.runtime" in content
    assert "PipelineAnalyzer" not in content
    assert "KnowledgeStorage" not in content
    assert "PersistentProjectKnowledge" not in content
    assert "FileKnowledgeStorage" not in content
