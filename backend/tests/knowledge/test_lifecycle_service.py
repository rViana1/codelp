from pathlib import Path

from core.project import Project, ProjectMetadata

from app.knowledge.lifecycle import KnowledgeLifecycleService

from app.knowledge.models import (
    PersistentKnowledgeMetadata,
    PersistentProjectKnowledge,
)


class FakeLoader:

    def __init__(self, knowledge=None):
        self.knowledge = knowledge

    def load(self, project_id):
        return self.knowledge


class FakeRestorer:

    def restore(
        self,
        project,
        knowledge,
    ):
        project.diagnostics.append(
            "restored"
        )
        return project


class FakePersistence:

    def persist(
        self,
        project,
    ):
        return PersistentProjectKnowledge(
            metadata=project.metadata
        )


def create_project(tmp_path):

    return Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=Path(tmp_path),
        )
    )


def test_prepare_without_previous_knowledge(
    tmp_path,
):

    project = create_project(
        tmp_path
    )

    service = KnowledgeLifecycleService(
        FakeLoader(),
        FakeRestorer(),
        FakePersistence(),
    )

    result = service.prepare(
        project
    )

    assert result is project
    assert result.diagnostics == []


def test_prepare_restores_previous_knowledge(
    tmp_path,
):

    project = create_project(
        tmp_path
    )

    service = KnowledgeLifecycleService(
        FakeLoader(
            PersistentProjectKnowledge(
                metadata=PersistentKnowledgeMetadata(
                    project_id="demo"
                )
            )
        ),
        FakeRestorer(),
        FakePersistence(),
    )

    result = service.prepare(
        project
    )

    assert "restored" in result.diagnostics
