from datetime import datetime, timezone

from app.knowledge.mapper import KnowledgeMapper
from app.knowledge.models import (
    PersistentKnowledgeMetadata,
    PersistentProjectKnowledge,
)

from core.project import Project, ProjectMetadata


def create_project(tmp_path):
    return Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=tmp_path,
        )
    )


def test_metadata_preserves_created_at_and_updates_updated_at(
    tmp_path,
):
    project = create_project(
        tmp_path
    )

    original_created_at = datetime(
        2025,
        1,
        1,
        tzinfo=timezone.utc,
    )

    original_updated_at = datetime(
        2025,
        1,
        2,
        tzinfo=timezone.utc,
    )

    previous = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo",
            created_at=original_created_at,
            updated_at=original_updated_at,
        )
    )

    result = KnowledgeMapper.from_project(
        project,
        project_id="demo",
        previous=previous,
    )

    assert result.metadata.created_at == original_created_at

    assert result.metadata.updated_at >= original_updated_at
