from app.knowledge.storage import (
    InMemoryKnowledgeStorage,
)

from app.knowledge.file_storage import (
    FileKnowledgeStorage,
)

from app.knowledge.models import (
    PersistentProjectKnowledge,
    PersistentKnowledgeMetadata,
)


def create_knowledge():

    return PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="replaceable-project"
        )
    )


def verify_storage_contract(
    storage,
):

    knowledge = create_knowledge()

    storage.save(
        knowledge
    )

    loaded = storage.load(
        "replaceable-project"
    )

    assert loaded is not None

    assert (
        loaded.metadata.project_id
        ==
        "replaceable-project"
    )


def test_in_memory_storage_is_replaceable(
):

    storage = InMemoryKnowledgeStorage()

    verify_storage_contract(
        storage
    )


def test_file_storage_is_replaceable(
    tmp_path,
):

    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    verify_storage_contract(
        storage
    )