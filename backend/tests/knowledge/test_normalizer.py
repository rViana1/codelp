from app.knowledge.models import (
    PersistentKnowledgeMetadata,
    PersistentProjectConfiguration,
    PersistentProjectKnowledge,
    PersistentFileIdentity,
    PersistentFileFingerprint,
    PersistentFileLocation,
    PersistentSymbolIdentity,
    PersistentChunkIdentity,
)

from app.knowledge.normalizer import KnowledgeNormalizer


def create_knowledge():
    return PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo"
        ),
        files=[
            PersistentFileIdentity(
                file_id="b.py",
                locations=[
                    PersistentFileLocation(
                        path="b.py",
                        first_seen="2026-01-01T00:00:00Z",
                        last_seen="2026-01-01T00:00:00Z",
                    )
                ],
                fingerprints=[
                    PersistentFileFingerprint(
                        content_hash="b",
                        size_bytes=1,
                        generated_at="2026-01-01T00:00:00Z",
                        last_seen="2026-01-01T00:00:00Z",
                    )
                ],
            ),
            PersistentFileIdentity(
                file_id="a.py",
                locations=[
                    PersistentFileLocation(
                        path="a.py",
                        first_seen="2026-01-01T00:00:00Z",
                        last_seen="2026-01-01T00:00:00Z",
                    )
                ],
                fingerprints=[
                    PersistentFileFingerprint(
                        content_hash="a",
                        size_bytes=1,
                        generated_at="2026-01-01T00:00:00Z",
                        last_seen="2026-01-01T00:00:00Z",
                    )
                ],
            ),
        ],
        symbols=[
            PersistentSymbolIdentity(
                symbol_id="b.symbol",
                file_id="b.py",
                name="b",
                symbol_type="function",
            ),
            PersistentSymbolIdentity(
                symbol_id="a.symbol",
                file_id="a.py",
                name="a",
                symbol_type="function",
            ),
        ],
        chunks=[
            PersistentChunkIdentity(
                chunk_id="chunk-b",
                symbol_id="b.symbol",
                content_hash="b",
            ),
            PersistentChunkIdentity(
                chunk_id="chunk-a",
                symbol_id="a.symbol",
                content_hash="a",
            ),
        ],
    )


def test_normalizer_sorts_collections():
    knowledge = create_knowledge()

    normalizer = KnowledgeNormalizer()

    result = normalizer.normalize(
        knowledge
    )

    assert [
        file.file_id
        for file in result.files
    ] == [
        "a.py",
        "b.py",
    ]

    assert [
        symbol.symbol_id
        for symbol in result.symbols
    ] == [
        "a.symbol",
        "b.symbol",
    ]

    assert [
        chunk.chunk_id
        for chunk in result.chunks
    ] == [
        "chunk-a",
        "chunk-b",
    ]


def test_normalizer_does_not_modify_original():
    knowledge = create_knowledge()

    normalizer = KnowledgeNormalizer()

    normalizer.normalize(
        knowledge
    )

    assert [
        file.file_id
        for file in knowledge.files
    ] == [
        "b.py",
        "a.py",
    ]


def test_normalizer_preserves_configuration():
    knowledge = create_knowledge()
    knowledge.configuration = PersistentProjectConfiguration(
        follow_symlinks=True,
        ignore_hidden=False,
        max_file_size_bytes=123,
        ignored_directories={"build"},
        ignored_extensions={".tmp"},
    )

    normalized = KnowledgeNormalizer().normalize(knowledge)

    assert normalized.configuration == knowledge.configuration
