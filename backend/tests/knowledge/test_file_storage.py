import json
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

    restored = storage.load(
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

    assert storage.exists(
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

    assert storage.load(
        "project-a"
    ).metadata.project_id == "project-a"

    assert storage.load(
        "project-b"
    ).metadata.project_id == "project-b"


def test_delete_project_knowledge(tmp_path):
    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    knowledge = create_knowledge()

    storage.save(knowledge)

    assert storage.exists(
        "test-project"
    )

    storage.delete(
        "test-project"
    )

    assert not storage.exists(
        "test-project"
    )


def test_missing_project_returns_none(tmp_path):
    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    result = storage.load(
        "unknown-project"
    )

    assert result is None
    
def test_storage_serialization_is_deterministic(
    tmp_path,
):
    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    knowledge = create_knowledge()

    storage.save(
        knowledge
    )

    first_content = (
        tmp_path / "test-project.json"
    ).read_text(
        encoding="utf-8"
    )

    storage.save(
        knowledge
    )

    second_content = (
        tmp_path / "test-project.json"
    ).read_text(
        encoding="utf-8"
    )

    assert first_content == second_content



def test_storage_normalizes_collection_order(
    tmp_path,
):
    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    knowledge = create_knowledge()

    knowledge.symbols = list(
        reversed(
            knowledge.symbols
        )
    )

    knowledge.chunks = list(
        reversed(
            knowledge.chunks
        )
    )

    storage.save(
        knowledge
    )

    restored = storage.load(
        "test-project"
    )

    assert restored is not None

    assert (
        restored.symbols[0].symbol_id
        ==
        "src/main.py::hello"
    )

    assert (
        restored.chunks[0].chunk_id
        ==
        "chunk-001"
    )
    
def test_atomic_write_does_not_leave_temporary_files(
    tmp_path,
):
    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    knowledge = create_knowledge()

    storage.save(
        knowledge
    )

    assert (
        tmp_path / "test-project.json"
    ).exists()

    assert not (
        tmp_path / "test-project.json.tmp"
    ).exists()