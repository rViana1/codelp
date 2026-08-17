import json
from pathlib import Path

from core.project.models import (
    Project,
    ProjectConfiguration,
    ProjectMetadata,
)

from app.knowledge.mapper import KnowledgeMapper


def test_persistent_project_knowledge_is_json_serializable():
    project = Project(
        metadata=ProjectMetadata(
            name="project",
            root_path=Path("/tmp/project"),
            description="Test project",
            version="1.0",
        ),
        configuration=ProjectConfiguration(
            follow_symlinks=True,
            ignore_hidden=False,
            max_file_size_bytes=123456,
            ignored_directories={
                ".git",
                "node_modules",
            },
            ignored_extensions={
                ".tmp",
                ".log",
            },
        ),
    )

    knowledge = KnowledgeMapper.from_project(
        project
    )

    serialized = knowledge.model_dump(
        mode="json"
    )

    encoded = json.dumps(
        serialized
    )

    assert isinstance(
        encoded,
        str,
    )

    assert json.loads(
        encoded
    ) == serialized
