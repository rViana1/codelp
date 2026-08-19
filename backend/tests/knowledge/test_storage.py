from app.knowledge.storage import InMemoryKnowledgeStorage
from app.knowledge.models import (
    PersistentProjectKnowledge,
    PersistentKnowledgeMetadata,
)


from datetime import datetime, timezone


def create_knowledge(project_id: str = "test-project"):
    now = datetime.now(timezone.utc)

    return PersistentProjectKnowledge(
        metadata={
            "project_id": project_id,
            "created_at": now,
            "updated_at": now,
        },
    )


def test_store_and_retrieve_knowledge():
    storage = InMemoryKnowledgeStorage()

    knowledge = create_knowledge()

    storage.save(knowledge)

    result = storage.get("test-project")

    assert result == knowledge


def test_storage_contains_project():
    storage = InMemoryKnowledgeStorage()

    knowledge = create_knowledge()

    storage.save(knowledge)

    assert storage.exists("test-project")


def test_storage_isolated_between_projects():
    storage = InMemoryKnowledgeStorage()

    project_a = create_knowledge("project-a")
    project_b = create_knowledge("project-b")

    storage.save(project_a)
    storage.save(project_b)

    assert storage.get("project-a") == project_a
    assert storage.get("project-b") == project_b


def test_delete_project_knowledge():
    storage = InMemoryKnowledgeStorage()

    knowledge = create_knowledge()

    storage.save(knowledge)

    storage.delete("test-project")

    assert not storage.exists("test-project")
