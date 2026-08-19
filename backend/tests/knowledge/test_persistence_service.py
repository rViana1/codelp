from pathlib import Path

from core.project import Project, ProjectMetadata

from app.knowledge.builder import KnowledgeBuilder
from app.knowledge.diff import ProjectChangeKind
from app.knowledge.file_storage import FileKnowledgeStorage
from app.knowledge.persistence import KnowledgePersistenceService
from app.knowledge.models import (
    PersistentKnowledgeMetadata,
    PersistentProjectKnowledge,
    PersistentSymbolIdentity,
)
from app.knowledge.storage import InMemoryKnowledgeStorage


class StaticBuilder:
    def __init__(self, knowledge):
        self.knowledge = knowledge

    def build(self, project, previous=None):
        return self.knowledge.model_copy(deep=True)


class PartialFailStorage(InMemoryKnowledgeStorage):
    def __init__(self):
        super().__init__()
        self.fail_next = False

    def save(self, knowledge):
        super().save(knowledge)
        if self.fail_next:
            self.fail_next = False
            raise RuntimeError("commit failed after partial write")


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

    assert project.knowledge_change_result is not None
    assert all(
        change.change_kind == ProjectChangeKind.NEW
        for change in project.knowledge_change_result.changed_elements
    )


def test_persistence_service_compares_with_persisted_previous_snapshot(
    tmp_path,
):
    source = tmp_path / "main.py"
    source.write_text("old", encoding="utf-8")
    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=Path(tmp_path),
        )
    )
    project.statistics.scanned_files = [source]
    storage = FileKnowledgeStorage(str(tmp_path / "knowledge"))
    service = KnowledgePersistenceService(KnowledgeBuilder(), storage)
    service.persist(project)

    source.write_text("new", encoding="utf-8")
    service.persist(project)

    report = project.knowledge_change_result
    assert len(report.modified_files) == 1
    assert report.modified_files[0].file_id == (
        storage.load(tmp_path.name).files[0].file_id
    )
    assert report.new_files == ()
    assert "knowledge_change_result" not in (
        storage.load(tmp_path.name).model_dump()
    )


def test_failed_commit_rolls_back_snapshot_and_runtime_report(tmp_path):
    project = Project(
        metadata=ProjectMetadata(name="demo", root_path=tmp_path / "demo")
    )
    previous = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(project_id="demo")
    )
    candidate = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(project_id="demo"),
        configuration=previous.configuration.model_copy(
            update={"ignore_hidden": False}
        ),
    )
    storage = PartialFailStorage()
    storage.save(previous)
    storage.fail_next = True
    project.knowledge_change_result = "previous-report"
    service = KnowledgePersistenceService(StaticBuilder(candidate), storage)

    try:
        service.persist(project)
    except RuntimeError as exc:
        assert "partial write" in str(exc)
    else:
        raise AssertionError("Commit failure was not propagated")

    assert storage.load("demo") == previous
    assert project.knowledge_change_result == "previous-report"


def test_validation_failure_does_not_touch_persisted_snapshot(tmp_path):
    project = Project(
        metadata=ProjectMetadata(name="demo", root_path=tmp_path / "demo")
    )
    previous = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(project_id="demo")
    )
    invalid = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(project_id="demo"),
        symbols=[
            PersistentSymbolIdentity(
                symbol_id="orphan",
                file_id="missing",
                name="orphan",
                symbol_type="function",
            )
        ],
    )
    storage = InMemoryKnowledgeStorage()
    storage.save(previous)
    service = KnowledgePersistenceService(StaticBuilder(invalid), storage)

    try:
        service.persist(project)
    except ValueError as exc:
        assert "unknown file" in str(exc)
    else:
        raise AssertionError("Invalid update was persisted")

    assert storage.load("demo") == previous
    assert project.knowledge_change_result is None
