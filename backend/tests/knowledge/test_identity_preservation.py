from pathlib import Path

from core.project import Project, ProjectMetadata

from app.knowledge.builder import KnowledgeBuilder
from app.knowledge.models import (
    PersistentFileIdentity,
    PersistentKnowledgeMetadata,
    PersistentProjectKnowledge,
)


def test_builder_preserves_existing_file_identity(tmp_path):

    file = tmp_path / "main.py"
    file.write_text(
        "print('hello')"
    )

    project = Project(
        metadata=ProjectMetadata(
            name="demo",
            root_path=tmp_path,
        )
    )

    project.statistics.scanned_files = [
        file
    ]

    previous = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        ),
        files=[
            PersistentFileIdentity(
                file_id="stable-id",
                path=str(file),
                content_hash="old-hash",
            )
        ],
    )

    result = KnowledgeBuilder().build(
        project,
        previous,
    )

    assert result.files[0].file_id == "stable-id"
