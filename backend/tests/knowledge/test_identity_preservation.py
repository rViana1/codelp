from datetime import datetime, timezone

from core.project import Project, ProjectMetadata

from app.knowledge.builder import KnowledgeBuilder
from app.knowledge.models import (
    PersistentFileFingerprint,
    PersistentFileIdentity,
    PersistentFileLocation,
    PersistentKnowledgeMetadata,
    PersistentProjectKnowledge,
)


def test_builder_preserves_existing_file_identity(tmp_path):

    file = tmp_path / "main.py"

    file.write_text(
        "print('hello')"
    )

    now = datetime.now(timezone.utc)

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
                locations=[
                    PersistentFileLocation(
                            path="main.py",
                        first_seen=now,
                        last_seen=now,
                        is_current=True,
                    )
                ],
                fingerprints=[
                    PersistentFileFingerprint(
                        content_hash="old-hash",
                        size_bytes=0,
                        generated_at=now,
                        last_seen=now,
                        is_current=True,
                    )
                ],
            )
        ],
    )

    result = KnowledgeBuilder().build(
        project,
        previous,
    )

    assert result.files[0].file_id == "stable-id"
