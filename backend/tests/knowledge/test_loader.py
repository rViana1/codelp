from app.knowledge.file_storage import FileKnowledgeStorage
from app.knowledge.loader import KnowledgeLoader
from app.knowledge.models import (
    PersistentKnowledgeMetadata,
    PersistentProjectKnowledge,
)


def test_loader_returns_existing_knowledge(tmp_path):

    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="project-a"
        )
    )

    storage.save(
        knowledge
    )

    loader = KnowledgeLoader(
        storage
    )

    result = loader.load(
        "project-a"
    )

    assert result is not None
    assert result.metadata.project_id == "project-a"


def test_loader_returns_none_when_missing(tmp_path):

    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    loader = KnowledgeLoader(
        storage
    )

    result = loader.load(
        "unknown"
    )

    assert result is None
