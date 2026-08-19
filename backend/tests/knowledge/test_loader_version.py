from app.knowledge.file_storage import FileKnowledgeStorage
from app.knowledge.loader import KnowledgeLoader
from app.knowledge.models import (
    PersistentKnowledgeMetadata,
    PersistentProjectKnowledge,
)


def test_loader_accepts_current_version(tmp_path):

    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    storage.save(
        PersistentProjectKnowledge(
            metadata=PersistentKnowledgeMetadata(
                    project_id="project-a",
                    version="2.0",
            )
        )
    )

    loader = KnowledgeLoader(
        storage
    )

    result = loader.load(
        "project-a"
    )

    assert result is not None



def test_loader_rejects_incompatible_version(tmp_path):

    storage = FileKnowledgeStorage(
        str(tmp_path)
    )

    storage.save(
        PersistentProjectKnowledge(
            metadata=PersistentKnowledgeMetadata(
                    project_id="project-a",
                    version="1.0",
            )
        )
    )

    loader = KnowledgeLoader(
        storage
    )

    try:
        loader.load(
            "project-a"
        )

        assert False

    except ValueError as error:

        assert "Unsupported knowledge version" in str(error)
