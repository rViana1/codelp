from datetime import datetime, timedelta, timezone

import pytest

from app.knowledge.models import (
    PersistentChunkIdentity,
    PersistentEmbeddingMetadata,
    PersistentFileFingerprint,
    PersistentFileIdentity,
    PersistentFileLocation,
    PersistentKnowledgeMetadata,
    PersistentProjectKnowledge,
    PersistentRetrievalMetadata,
    PersistentSymbolIdentity,
)
from app.knowledge.update import KnowledgeUpdateEngine
from app.knowledge.validator import KnowledgeValidator


T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
T1 = T0 + timedelta(days=1)


def file(file_id, path, content_hash, timestamp=T0):
    return PersistentFileIdentity(
        file_id=file_id,
        locations=[
            PersistentFileLocation(
                path=path,
                first_seen=timestamp,
                last_seen=timestamp,
                is_current=True,
            )
        ],
        fingerprints=[
            PersistentFileFingerprint(
                content_hash=content_hash,
                size_bytes=1,
                generated_at=timestamp,
                last_seen=timestamp,
                is_current=True,
            )
        ],
    )


def knowledge(
    *,
    project_id="demo",
    timestamp=T0,
    files=None,
    symbols=None,
    chunks=None,
    embeddings=None,
    retrieval=None,
):
    return PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id=project_id,
            created_at=timestamp,
            updated_at=timestamp,
        ),
        files=files or [],
        symbols=symbols or [],
        chunks=chunks or [],
        embeddings=embeddings or [],
        retrieval=retrieval or [],
    )


def symbol(symbol_id, file_id, name):
    return PersistentSymbolIdentity(
        symbol_id=symbol_id,
        file_id=file_id,
        name=name,
        symbol_type="function",
    )


def chunk(chunk_id, symbol_id, content_hash):
    return PersistentChunkIdentity(
        chunk_id=chunk_id,
        symbol_id=symbol_id,
        content_hash=content_hash,
    )


def embedding(chunk_id, value):
    return PersistentEmbeddingMetadata(
        chunk_id=chunk_id,
        provider="fake",
        embedding_hash=value,
    )


def retrieval(chunk_id, score):
    return PersistentRetrievalMetadata(
        chunk_id=chunk_id,
        query_hash="query",
        score=score,
    )


def snapshots():
    previous = knowledge(
        files=[
            file("file-1", "old.py", "old"),
            file("file-removed", "removed.py", "removed"),
        ],
        symbols=[
            symbol("symbol-stable", "file-1", "stable"),
            symbol("symbol-modified", "file-1", "before"),
            symbol("symbol-obsolete", "file-removed", "obsolete"),
        ],
        chunks=[
            chunk("chunk-stable", "symbol-stable", "same"),
            chunk("chunk-modified", "symbol-modified", "old"),
            chunk("chunk-obsolete", "symbol-obsolete", "obsolete"),
        ],
        embeddings=[
            embedding("chunk-stable", "same"),
            embedding("chunk-modified", "old"),
            embedding("chunk-obsolete", "obsolete"),
        ],
        retrieval=[
            retrieval("chunk-stable", 1.0),
            retrieval("chunk-modified", 0.5),
            retrieval("chunk-obsolete", 0.1),
        ],
    )
    current = knowledge(
        timestamp=T1,
        files=[
            file("file-new", "new.py", "new", T1),
            file("file-1", "src/new.py", "changed", T1),
        ],
        symbols=[
            symbol("symbol-new", "file-new", "new"),
            symbol("symbol-modified", "file-1", "after"),
            symbol("symbol-stable", "file-1", "stable"),
        ],
        chunks=[
            chunk("chunk-new", "symbol-new", "new"),
            chunk("chunk-modified", "symbol-modified", "changed"),
            chunk("chunk-stable", "symbol-stable", "same"),
        ],
        embeddings=[
            embedding("chunk-new", "new"),
            embedding("chunk-modified", "changed"),
            embedding("chunk-stable", "same"),
        ],
        retrieval=[
            retrieval("chunk-new", 0.2),
            retrieval("chunk-modified", 0.9),
            retrieval("chunk-stable", 1.0),
        ],
    )
    return previous, current


def test_merge_adds_updates_removes_and_preserves_knowledge():
    previous, current = snapshots()

    merged = KnowledgeUpdateEngine().merge(previous, current)

    assert [item.file_id for item in merged.files] == [
        "file-1",
        "file-new",
        "file-removed",
    ]
    file_one = merged.files[0]
    assert [(item.path, item.is_current) for item in file_one.locations] == [
        ("old.py", False),
        ("src/new.py", True),
    ]
    assert [item.content_hash for item in file_one.fingerprints] == [
        "old",
        "changed",
    ]
    removed = merged.files[-1]
    assert not any(item.is_current for item in removed.locations)
    assert not any(item.is_current for item in removed.fingerprints)

    assert [item.symbol_id for item in merged.symbols] == [
        "symbol-modified",
        "symbol-new",
        "symbol-stable",
    ]
    assert next(
        item for item in merged.symbols
        if item.symbol_id == "symbol-modified"
    ).name == "after"
    assert all(
        item.symbol_id != "symbol-obsolete" for item in merged.symbols
    )
    assert next(
        item for item in merged.chunks
        if item.chunk_id == "chunk-modified"
    ).content_hash == "changed"
    assert all(item.chunk_id != "chunk-obsolete" for item in merged.chunks)
    assert merged.metadata.created_at == previous.metadata.created_at
    assert merged.metadata.updated_at == current.metadata.updated_at
    KnowledgeValidator().validate(merged)


def test_merge_is_deterministic_for_reordered_inputs():
    previous, current = snapshots()
    engine = KnowledgeUpdateEngine()

    first = engine.merge(previous, current)
    reversed_previous = previous.model_copy(
        update={
            field: list(reversed(getattr(previous, field)))
            for field in (
                "files",
                "symbols",
                "chunks",
                "embeddings",
                "retrieval",
            )
        },
        deep=True,
    )
    reversed_current = current.model_copy(
        update={
            field: list(reversed(getattr(current, field)))
            for field in (
                "files",
                "symbols",
                "chunks",
                "embeddings",
                "retrieval",
            )
        },
        deep=True,
    )

    second = engine.merge(reversed_previous, reversed_current)

    assert first == second


def test_first_snapshot_is_normalized_without_mutating_candidate():
    _, current = snapshots()
    current.files.reverse()
    current.symbols.reverse()
    input_snapshot = current.model_copy(deep=True)

    merged = KnowledgeUpdateEngine().merge(None, current)

    assert [item.file_id for item in merged.files] == sorted(
        item.file_id for item in merged.files
    )
    assert current == input_snapshot
    assert merged is not current


def test_merge_rejects_snapshots_from_different_projects():
    previous, current = snapshots()
    current.metadata.project_id = "other"

    with pytest.raises(ValueError, match="different projects"):
        KnowledgeUpdateEngine().merge(previous, current)


def test_merge_preserves_earliest_history_and_latest_observation():
    previous = knowledge(files=[file("file-1", "main.py", "same", T0)])
    current = knowledge(
        timestamp=T1,
        files=[file("file-1", "main.py", "same", T1)],
    )

    merged = KnowledgeUpdateEngine().merge(previous, current)

    location = merged.files[0].locations[0]
    fingerprint = merged.files[0].fingerprints[0]
    assert location.first_seen == T0
    assert location.last_seen == T1
    assert fingerprint.generated_at == T0
    assert fingerprint.last_seen == T1


def test_merge_rejects_duplicate_candidate_identities():
    duplicate = symbol("duplicate", "file-1", "same")
    current = knowledge(
        files=[file("file-1", "main.py", "hash")],
        symbols=[duplicate, duplicate.model_copy(deep=True)],
    )

    with pytest.raises(ValueError, match="Duplicate knowledge identity"):
        KnowledgeUpdateEngine().merge(None, current)
