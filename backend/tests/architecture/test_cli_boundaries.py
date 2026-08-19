from pathlib import Path


def test_cli_uses_runtime_and_does_not_assemble_pipeline_or_storage():
    content = Path("backend/app/cli/main.py").read_text(encoding="utf-8")

    assert "app.runtime" in content
    assert "PipelineAnalyzer" not in content
    assert "KnowledgeStorage" not in content
    assert "FileKnowledgeStorage" not in content
    assert "KnowledgeLifecycleService" not in content
