from app.knowledge.file_storage import FileKnowledgeStorage
from app.knowledge.models import (
    PersistentKnowledgeMetadata,
    PersistentProjectKnowledge,
    PersistentSymbolIdentity,
    PersistentChunkIdentity,
)


def create_knowledge(project_id: str = "test-project"):
    return PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id=project_id
        ),
        symbols=[
            PersistentSymbolIdentity(
                symbol_id="src/main.py::hello",
                file_id="src/main.py",
                name="hello",
                symbol_type="function",
            )
        ],
        chunks=[
            PersistentChunkIdentity(
                chunk_id="chunk-001",
                symbol_id="src/main.py::hello",
                content_hash="hash123",
            )
        ],
    )


def test_save_and_reload_knowledge(tmp_path):
    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    knowledge = create_knowledge()

    storage.save(knowledge)

    restored = storage.get(
        "test-project"
    )

    assert restored is not None
    assert restored.metadata.project_id == "test-project"
    assert restored.symbols[0].symbol_id == "src/main.py::hello"
    assert restored.chunks[0].chunk_id == "chunk-001"


def test_storage_contains_project(tmp_path):
    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    knowledge = create_knowledge()

    storage.save(knowledge)

    assert storage.contains(
        "test-project"
    )


def test_storage_isolated_between_projects(tmp_path):
    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    project_a = create_knowledge(
        "project-a"
    )

    project_b = create_knowledge(
        "project-b"
    )

    storage.save(project_a)
    storage.save(project_b)

    assert storage.get(
        "project-a"
    ).metadata.project_id == "project-a"

    assert storage.get(
        "project-b"
    ).metadata.project_id == "project-b"


def test_delete_project_knowledge(tmp_path):
    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    knowledge = create_knowledge()

    storage.save(knowledge)

    assert storage.contains(
        "test-project"
    )

    storage.delete(
        "test-project"
    )

    assert not storage.contains(
        "test-project"
    )


def test_missing_project_returns_none(tmp_path):
    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    result = storage.get(
        "unknown-project"
    )

    assert result is None
