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


def test_service_save_and_load(tmp_path):
    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    service = KnowledgeService(
        storage
    )

    knowledge = create_knowledge()

    service.save(
        knowledge
    )

    result = service.load(
        "test-project"
    )

    assert result is not None
    assert result.metadata.project_id == "test-project"


def test_service_exists(tmp_path):
    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    service = KnowledgeService(
        storage
    )

    service.save(
        create_knowledge()
    )

    assert service.exists(
        "test-project"
    )


def test_service_remove(tmp_path):
    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    service = KnowledgeService(
        storage
    )

    service.save(
        create_knowledge()
    )

    service.remove(
        "test-project"
    )

    assert not service.exists(
        "test-project"
    )


def test_service_preserves_project_identity(tmp_path):
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

    restored = service.load(
        "project-a"
    )

    assert restored.metadata.project_id == "project-a"
