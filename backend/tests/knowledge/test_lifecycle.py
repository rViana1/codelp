from app.knowledge.file_storage import FileKnowledgeStorage
from app.knowledge.models import (
    PersistentKnowledgeMetadata,
    PersistentProjectKnowledge,
)
from app.knowledge.service import KnowledgeService


def create_knowledge(project_id: str = "test-project"):
    return PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id=project_id
        )
    )


def test_get_or_create_creates_missing_knowledge(tmp_path):
    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    service = KnowledgeService(
        storage
    )

    result = service.get_or_create(
        "test-project"
    )

    assert result is not None
    assert result.metadata.project_id == "test-project"

    assert service.exists(
        "test-project"
    )


def test_get_or_create_loads_existing_knowledge(tmp_path):
    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    service = KnowledgeService(
        storage
    )

    knowledge = create_knowledge(
        "project-a"
    )

    service.save(
        knowledge
    )

    result = service.get_or_create(
        "project-a"
    )

    assert result.metadata.project_id == "project-a"


def test_get_or_create_preserves_existing_identity(tmp_path):
    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    service = KnowledgeService(
        storage
    )

    original = create_knowledge(
        "project-a"
    )

    service.save(
        original
    )

    restored = service.get_or_create(
        "project-a"
    )

    assert restored.metadata.project_id == original.metadata.project_id
    assert restored.metadata.created_at == original.metadata.created_at


def test_update_replaces_existing_knowledge(tmp_path):
    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    service = KnowledgeService(
        storage
    )

    original = create_knowledge(
        "project-a"
    )

    service.save(
        original
    )

    updated = create_knowledge(
        "project-a"
    )

    updated.metadata.updated_at = updated.metadata.updated_at.replace(
        year=2030
    )

    service.update(
        updated
    )

    result = service.load(
        "project-a"
    )

    assert result is not None
    assert result.metadata.project_id == "project-a"
    assert result.metadata.updated_at.year == 2030
