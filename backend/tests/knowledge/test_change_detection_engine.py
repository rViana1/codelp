from datetime import datetime, timezone

from app.knowledge.diff import (
    ChangeDetectionEngine,
    ProjectChangeKind,
    ProjectElementKind,
)
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


NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def file(file_id: str, path: str, content_hash: str):
    return PersistentFileIdentity(
        file_id=file_id,
        locations=[
            PersistentFileLocation(
                path=path,
                first_seen=NOW,
                last_seen=NOW,
                is_current=True,
            )
        ],
        fingerprints=[
            PersistentFileFingerprint(
                content_hash=content_hash,
                size_bytes=1,
                generated_at=NOW,
                last_seen=NOW,
                is_current=True,
            )
        ],
    )


def knowledge(*, files=None, symbols=None, chunks=None, embeddings=None,
              retrieval=None):
    return PersistentProjectKnowledge(
        metadata=PersistentKnowledgeMetadata(
            project_id="demo",
            created_at=NOW,
            updated_at=NOW,
        ),
        files=files or [],
        symbols=symbols or [],
        chunks=chunks or [],
        embeddings=embeddings or [],
        retrieval=retrieval or [],
    )


def test_detects_every_file_change_using_stable_identity():
    previous = knowledge(
        files=[
            file("unchanged", "same.py", "a"),
            file("modified", "edit.py", "old"),
            file("moved", "main.py", "b"),
            file("renamed", "old.py", "c"),
            file("both", "old/old.py", "d"),
            file("removed", "removed.py", "e"),
        ]
    )
    current = knowledge(
        files=[
            file("new", "new.py", "f"),
            file("unchanged", "same.py", "a"),
            file("modified", "edit.py", "new"),
            file("moved", "src/main.py", "b"),
            file("renamed", "new_name.py", "c"),
            file("both", "new/new_name.py", "d"),
        ]
    )

    report = ChangeDetectionEngine().compare(previous, current)

    assert tuple(item.file_id for item in report.new_files) == ("new",)
    assert tuple(item.file_id for item in report.removed_files) == (
        "removed",
    )
    assert tuple(item.file_id for item in report.moved_files) == ("moved",)
    assert tuple(item.file_id for item in report.renamed_files) == (
        "renamed",
    )
    assert tuple(
        item.file_id for item in report.moved_and_renamed_files
    ) == ("both",)
    assert tuple(item.file_id for item in report.modified_files) == (
        "modified",
    )
    assert tuple(item.file_id for item in report.unchanged_files) == (
        "unchanged",
    )

    changes = {
        item.element_id: item.change_kind
        for item in report.changed_elements
        if item.element_kind == ProjectElementKind.FILE
    }
    assert changes == {
        "both": ProjectChangeKind.MOVED_AND_RENAMED,
        "modified": ProjectChangeKind.MODIFIED,
        "moved": ProjectChangeKind.MOVED,
        "new": ProjectChangeKind.NEW,
        "removed": ProjectChangeKind.REMOVED,
        "renamed": ProjectChangeKind.RENAMED,
    }


def test_defines_changed_unchanged_invalidated_and_reusable_elements():
    previous = knowledge(
        files=[file("file-1", "main.py", "same")],
        symbols=[
            PersistentSymbolIdentity(
                symbol_id="symbol-stable",
                file_id="file-1",
                name="stable",
                symbol_type="function",
            ),
            PersistentSymbolIdentity(
                symbol_id="symbol-removed",
                file_id="file-1",
                name="removed",
                symbol_type="function",
            ),
        ],
        chunks=[
            PersistentChunkIdentity(
                chunk_id="chunk-stable",
                symbol_id="symbol-stable",
                content_hash="same",
            ),
            PersistentChunkIdentity(
                chunk_id="chunk-modified",
                symbol_id="symbol-stable",
                content_hash="old",
            ),
        ],
        embeddings=[
            PersistentEmbeddingMetadata(
                chunk_id="chunk-stable",
                provider="fake",
                embedding_hash="same",
            ),
            PersistentEmbeddingMetadata(
                chunk_id="chunk-modified",
                provider="fake",
                embedding_hash="same",
            ),
        ],
        retrieval=[
            PersistentRetrievalMetadata(
                chunk_id="chunk-stable",
                query_hash="query",
                score=1.0,
            ),
            PersistentRetrievalMetadata(
                chunk_id="chunk-modified",
                query_hash="query",
                score=1.0,
            ),
        ],
    )
    current = knowledge(
        files=[file("file-1", "main.py", "same")],
        symbols=[
            PersistentSymbolIdentity(
                symbol_id="symbol-stable",
                file_id="file-1",
                name="stable",
                symbol_type="function",
            ),
            PersistentSymbolIdentity(
                symbol_id="symbol-new",
                file_id="file-1",
                name="new",
                symbol_type="function",
            ),
        ],
        chunks=[
            PersistentChunkIdentity(
                chunk_id="chunk-stable",
                symbol_id="symbol-stable",
                content_hash="same",
            ),
            PersistentChunkIdentity(
                chunk_id="chunk-modified",
                symbol_id="symbol-stable",
                content_hash="new",
            ),
        ],
        embeddings=[
            PersistentEmbeddingMetadata(
                chunk_id="chunk-stable",
                provider="fake",
                embedding_hash="same",
            ),
            PersistentEmbeddingMetadata(
                chunk_id="chunk-modified",
                provider="fake",
                embedding_hash="same",
            ),
        ],
        retrieval=[
            PersistentRetrievalMetadata(
                chunk_id="chunk-stable",
                query_hash="query",
                score=1.0,
            ),
            PersistentRetrievalMetadata(
                chunk_id="chunk-modified",
                query_hash="query",
                score=1.0,
            ),
        ],
    )

    report = ChangeDetectionEngine().compare(previous, current)
    changed = {
        (item.element_kind, item.element_id, item.change_kind)
        for item in report.changed_elements
    }
    invalidated = {
        (item.element_kind, item.element_id, item.reason)
        for item in report.invalidated_elements
    }
    reusable = {
        (item.element_kind, item.element_id)
        for item in report.reusable_elements
    }

    assert (
        ProjectElementKind.SYMBOL,
        "symbol-new",
        ProjectChangeKind.NEW,
    ) in changed
    assert (
        ProjectElementKind.SYMBOL,
        "symbol-removed",
        ProjectChangeKind.REMOVED,
    ) in changed
    assert (
        ProjectElementKind.CHUNK,
        "chunk-modified",
        "modified",
    ) in invalidated
    assert (
        ProjectElementKind.EMBEDDING,
        "chunk-modified::fake",
        "dependency_invalidated",
    ) in invalidated
    assert (
        ProjectElementKind.RETRIEVAL,
        "chunk-modified::query",
        "dependency_invalidated",
    ) in invalidated
    assert (
        ProjectElementKind.CHUNK,
        "chunk-stable",
    ) in reusable
    assert (
        ProjectElementKind.EMBEDDING,
        "chunk-stable::fake",
    ) in reusable
    assert (
        ProjectElementKind.RETRIEVAL,
        "chunk-stable::query",
    ) in reusable


def test_change_report_is_deterministic_for_shuffled_snapshots():
    previous_files = [
        file("b", "b.py", "old"),
        file("a", "a.py", "same"),
    ]
    current_files = [
        file("c", "c.py", "new"),
        file("b", "b.py", "new"),
        file("a", "a.py", "same"),
    ]
    engine = ChangeDetectionEngine()

    first = engine.compare(
        knowledge(files=previous_files),
        knowledge(files=current_files),
    )
    second = engine.compare(
        knowledge(files=list(reversed(previous_files))),
        knowledge(files=list(reversed(current_files))),
    )

    assert first == second


def test_first_execution_reports_all_current_elements_as_new():
    current = knowledge(files=[file("file-1", "main.py", "hash")])

    report = ChangeDetectionEngine().compare(None, current)

    assert report.new_files[0].file_id == "file-1"
    assert report.unchanged_elements == ()
    assert report.reusable_elements == ()
