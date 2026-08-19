from datetime import datetime, timezone

import pytest

from app.knowledge.identity import (
    FileIdentityDecisionKind,
    FileObservation,
)
from app.knowledge.models import (
    PersistentChunkIdentity,
    PersistentEmbeddingMetadata,
    PersistentFileFingerprint,
    PersistentFileIdentity,
    PersistentFileLocation,
    PersistentSymbolIdentity,
)
from app.knowledge.tracking import IdentityTrackingEngine


NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def previous_file(
    file_id: str,
    path: str,
    content_hash: str,
) -> PersistentFileIdentity:
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


def observation(path: str, content_hash: str) -> FileObservation:
    return FileObservation(
        path=path,
        content_hash=content_hash,
        size_bytes=1,
    )


def track(
    *,
    observations,
    previous_files=None,
    source_symbols=None,
    previous_symbols=None,
    previous_chunks=None,
    previous_embeddings=None,
):
    return IdentityTrackingEngine().track(
        project_id="demo",
        observations=observations,
        source_symbols=source_symbols or [],
        previous_files=previous_files or [],
        previous_symbols=previous_symbols or [],
        previous_chunks=previous_chunks or [],
        previous_embeddings=previous_embeddings or [],
        now=NOW,
    )


def test_tracks_known_entity_and_associates_current_path():
    result = track(
        previous_files=[
            previous_file("file-1", "main.py", "old")
        ],
        observations=[observation("main.py", "new")],
        previous_symbols=[
            PersistentSymbolIdentity(
                symbol_id="symbol-1",
                file_id="file-1",
                name="hello",
                symbol_type="function",
            )
        ],
        previous_chunks=[
            PersistentChunkIdentity(
                chunk_id="chunk-1",
                symbol_id="symbol-1",
                content_hash="chunk-hash",
            )
        ],
        previous_embeddings=[
            PersistentEmbeddingMetadata(
                chunk_id="chunk-1",
                provider="fake",
                embedding_hash="embedding-hash",
            )
        ],
    )

    assert result.known_file_ids == ("file-1",)
    assert result.known_symbol_ids == ("symbol-1",)
    assert result.known_chunk_ids == ("chunk-1",)
    assert result.known_embedding_identities == (
        ("chunk-1", "fake"),
    )
    assert result.files[0].file_id == "file-1"
    assert result.file_decisions[0].kind == (
        FileIdentityDecisionKind.MODIFIED
    )
    assert result.file_decisions[0].confidence == 1.0


@pytest.mark.parametrize(
    ("destination", "expected_kind"),
    [
        ("src/main.py", FileIdentityDecisionKind.MOVED),
        ("renamed.py", FileIdentityDecisionKind.RENAMED),
        (
            "src/renamed.py",
            FileIdentityDecisionKind.MOVED_AND_RENAMED,
        ),
    ],
)
def test_detects_probable_move_or_rename(
    destination,
    expected_kind,
):
    result = track(
        previous_files=[
            previous_file("file-1", "main.py", "same")
        ],
        observations=[observation(destination, "same")],
    )

    decision = result.file_decisions[0]
    assert decision.kind == expected_kind
    assert decision.file_id == "file-1"
    assert decision.previous_path == "main.py"
    assert decision.confidence == 0.9
    assert [
        (location.path, location.is_current)
        for location in result.files[0].locations
    ] == [
        ("main.py", False),
        (destination, True),
    ]


def test_detects_duplicated_file_contents_deterministically():
    result = track(
        observations=[
            observation("b.py", "same"),
            observation("a.py", "same"),
            observation("other.py", "different"),
        ]
    )

    assert len(result.duplicated_file_contents) == 1
    duplicate = result.duplicated_file_contents[0]
    assert duplicate.content_hash == "same"
    assert duplicate.paths == ("a.py", "b.py")


def test_detects_duplicated_symbols_across_files():
    result = track(
        observations=[
            observation("a.py", "a"),
            observation("b.py", "b"),
        ],
        source_symbols=[
            PersistentSymbolIdentity(
                symbol_id="a.py::hello",
                file_id="a.py",
                name="hello",
                symbol_type="function",
            ),
            PersistentSymbolIdentity(
                symbol_id="b.py::hello",
                file_id="b.py",
                name="hello",
                symbol_type="function",
            ),
        ],
    )

    assert len(result.duplicated_symbols) == 1
    duplicate = result.duplicated_symbols[0]
    assert duplicate.name == "hello"
    assert duplicate.symbol_type == "function"
    assert len(duplicate.file_ids) == 2
    assert len(duplicate.symbol_ids) == 2


def test_ambiguous_fingerprint_produces_conflict_and_new_identity():
    result = track(
        previous_files=[
            previous_file("file-b", "b.py", "same"),
            previous_file("file-a", "a.py", "same"),
        ],
        observations=[observation("c.py", "same")],
    )

    conflict = result.conflicts[0]
    assert conflict.conflict_type == "ambiguous_fingerprint"
    assert conflict.candidate_file_ids == ("file-a", "file-b")
    assert conflict.resolution == "created_new_identity"
    current_file = next(
        file
        for file in result.files
        if any(location.is_current for location in file.locations)
    )
    assert current_file.file_id not in {"file-a", "file-b"}
    assert any(
        decision.kind == FileIdentityDecisionKind.CONFLICT_NEW
        for decision in result.file_decisions
    )


def test_ambiguous_current_path_uses_same_conflict_policy():
    result = track(
        previous_files=[
            previous_file("file-b", "main.py", "b"),
            previous_file("file-a", "main.py", "a"),
        ],
        observations=[observation("main.py", "a")],
    )

    assert result.conflicts[0].conflict_type == (
        "ambiguous_current_path"
    )
    assert result.conflicts[0].candidate_file_ids == (
        "file-a",
        "file-b",
    )


def test_resolution_result_is_independent_of_input_order():
    previous = [
        previous_file("file-b", "b.py", "b"),
        previous_file("file-a", "a.py", "a"),
    ]
    observations = [
        observation("b.py", "b"),
        observation("a.py", "a"),
    ]
    source_symbols = [
        PersistentSymbolIdentity(
            symbol_id="b.py::hello",
            file_id="b.py",
            name="hello",
            symbol_type="function",
        ),
        PersistentSymbolIdentity(
            symbol_id="a.py::hello",
            file_id="a.py",
            name="hello",
            symbol_type="function",
        ),
    ]

    first = track(
        previous_files=previous,
        observations=observations,
        source_symbols=source_symbols,
    )
    second = track(
        previous_files=list(reversed(previous)),
        observations=list(reversed(observations)),
        source_symbols=list(reversed(source_symbols)),
    )

    assert first == second
