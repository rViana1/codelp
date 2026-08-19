from pathlib import Path


def test_observability_has_no_source_or_persistence_dependencies():
    content = Path("backend/app/runtime/observability.py").read_text(
        encoding="utf-8"
    )

    assert "app.knowledge" not in content
    assert "CodeChunk" not in content
    assert "PersistentProjectKnowledge" not in content
