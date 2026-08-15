from pathlib import Path

from core.project import Project, ProjectMetadata

from app.knowledge.models import (
    PersistentKnowledgeMetadata,
    PersistentProjectKnowledge,
)

from app.knowledge.restorer import KnowledgeRestorer


def test_restorer_updates_project_state(tmp_path):

    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=Path(tmp_path),
        )
    )

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        )
    )

    restorer = KnowledgeRestorer()

    result = restorer.restore(
        project,
        knowledge,
    )

    assert result is project

    assert (
        "Restored knowledge for project demo"
        in project.diagnostics
    )
