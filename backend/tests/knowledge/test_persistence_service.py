from pathlib import Path

from core.project import Project, ProjectMetadata

from app.knowledge.builder import KnowledgeBuilder
from app.knowledge.file_storage import FileKnowledgeStorage
from app.knowledge.persistence import KnowledgePersistenceService


def test_persistence_service_saves_project_knowledge(
    tmp_path,
):

    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=Path(tmp_path),
        )
    )

    storage = FileKnowledgeStorage(
        str(tmp_path / "knowledge")
    )

    service = KnowledgePersistenceService(
        KnowledgeBuilder(),
        storage,
    )

    knowledge = service.persist(
        project
    )

    assert knowledge.metadata.project_id == tmp_path.name

    assert storage.contains(
        tmp_path.name
    )
