import pytest

from app.knowledge.models import (
    PersistentKnowledgeMetadata,
    PersistentProjectKnowledge,
    PersistentFileIdentity,
)

from app.knowledge.validator import KnowledgeValidator


def test_validator_accepts_valid_knowledge():

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        ),
        files=[
            PersistentFileIdentity(
                file_id="file-1",
                path="main.py",
                content_hash="hash",
            )
        ],
    )

    KnowledgeValidator().validate(
        knowledge
    )


def test_validator_rejects_duplicate_file_identity():

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        ),
        files=[
            PersistentFileIdentity(
                file_id="file-1",
                path="a.py",
                content_hash="hash",
            ),
            PersistentFileIdentity(
                file_id="file-1",
                path="b.py",
                content_hash="hash",
            ),
        ],
    )

    with pytest.raises(ValueError):
        KnowledgeValidator().validate(
            knowledge
        )
