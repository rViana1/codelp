from app.knowledge.models import (
    PersistentKnowledgeMetadata,
    PersistentProjectKnowledge,
    PersistentFileIdentity,
    PersistentFileFingerprint,
    PersistentFileLocation,
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
                locations=[
                    PersistentFileLocation(
                        path="b.py",
                        first_seen="2026-01-01T00:00:00Z",
                        last_seen="2026-01-01T00:00:00Z",
                    )
                ],
                fingerprints=[
                    PersistentFileFingerprint(
                        content_hash="hash-b",
                        size_bytes=1,
                        generated_at="2026-01-01T00:00:00Z",
                        last_seen="2026-01-01T00:00:00Z",
                    )
                ],
            ),
            PersistentFileIdentity(
                file_id="a",
                locations=[
                    PersistentFileLocation(
                        path="a.py",
                        first_seen="2026-01-01T00:00:00Z",
                        last_seen="2026-01-01T00:00:00Z",
                    )
                ],
                fingerprints=[
                    PersistentFileFingerprint(
                        content_hash="hash-a",
                        size_bytes=1,
                        generated_at="2026-01-01T00:00:00Z",
                        last_seen="2026-01-01T00:00:00Z",
                    )
                ],
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
                locations=[
                    PersistentFileLocation(
                        path="b.py",
                        first_seen="2026-01-01T00:00:00Z",
                        last_seen="2026-01-01T00:00:00Z",
                    )
                ],
                fingerprints=[
                    PersistentFileFingerprint(
                        content_hash="hash-b",
                        size_bytes=1,
                        generated_at="2026-01-01T00:00:00Z",
                        last_seen="2026-01-01T00:00:00Z",
                    )
                ],
            ),
            PersistentFileIdentity(
                file_id="a",
                locations=[
                    PersistentFileLocation(
                        path="a.py",
                        first_seen="2026-01-01T00:00:00Z",
                        last_seen="2026-01-01T00:00:00Z",
                    )
                ],
                fingerprints=[
                    PersistentFileFingerprint(
                        content_hash="hash-a",
                        size_bytes=1,
                        generated_at="2026-01-01T00:00:00Z",
                        last_seen="2026-01-01T00:00:00Z",
                    )
                ],
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
