from pathlib import Path


def test_execution_manager_coordinates_runtime_without_domain_or_storage_logic():
    content = Path("backend/app/runtime/execution.py").read_text(encoding="utf-8")

    assert "core.project" not in content
    assert "app.knowledge" not in content
    assert "FileKnowledgeStorage" not in content
    assert "PipelineAnalyzer" not in content
