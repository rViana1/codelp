from app.knowledge.models import (
    PersistentKnowledgeMetadata,
    PersistentProjectKnowledge,
    PersistentFileIdentity,
)

from app.knowledge.normalizer import KnowledgeNormalizer


def test_normalizer_produces_deterministic_file_order():

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        ),
        files=[
            PersistentFileIdentity(
                file_id="b",
                path="b.py",
                content_hash="hash-b",
            ),
            PersistentFileIdentity(
                file_id="a",
                path="a.py",
                content_hash="hash-a",
            ),
        ],
    )

    normalized = KnowledgeNormalizer().normalize(
        knowledge
    )

    assert normalized.files[0].file_id == "a"
    assert normalized.files[1].file_id == "b"


def test_normalizer_does_not_mutate_original():

    knowledge = PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        ),
        files=[
            PersistentFileIdentity(
                file_id="b",
                path="b.py",
                content_hash="hash-b",
            ),
            PersistentFileIdentity(
                file_id="a",
                path="a.py",
                content_hash="hash-a",
            ),
        ],
    )

    original_order = [
        file.file_id
        for file in knowledge.files
    ]

    KnowledgeNormalizer().normalize(
        knowledge
    )

    assert [
        file.file_id
        for file in knowledge.files
    ] == original_order
