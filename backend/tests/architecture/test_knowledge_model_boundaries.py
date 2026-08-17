from pathlib import Path


def test_persistent_knowledge_model_does_not_depend_on_storage():
    """
    Persistent knowledge models must not depend on storage technology.
    """

    file = Path(
        "backend/app/knowledge/models.py"
    )

    content = file.read_text(
        encoding="utf-8"
    )

    forbidden_dependencies = [
        "KnowledgeStorage",
        "FileKnowledgeStorage",
        "InMemoryKnowledgeStorage",
        "json",
        "sqlite",
        "database",
    ]

    for dependency in forbidden_dependencies:
        assert dependency not in content
