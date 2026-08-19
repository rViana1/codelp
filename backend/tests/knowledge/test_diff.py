from app.knowledge.diff import KnowledgeDiff
from app.knowledge.models import (
    PersistentFileFingerprint,
    PersistentFileIdentity,
    PersistentFileLocation,
)


def create_file(
    path: str,
    file_hash: str,
) -> PersistentFileIdentity:

    return PersistentFileIdentity(
        file_id=path,
        locations=[
            PersistentFileLocation(
                path=path,
                first_seen="2026-01-01T00:00:00Z",
                last_seen="2026-01-01T00:00:00Z",
                is_current=True,
            )
        ],
        fingerprints=[
            PersistentFileFingerprint(
                content_hash=file_hash,
                size_bytes=len(file_hash),
                generated_at="2026-01-01T00:00:00Z",
                last_seen="2026-01-01T00:00:00Z",
                is_current=True,
            )
        ],
    )


def current_path(
    file: PersistentFileIdentity,
) -> str:
    return next(
        location.path
        for location in file.locations
        if location.is_current
    )


def current_content_hash(
    file: PersistentFileIdentity,
) -> str:
    return next(
        fingerprint.content_hash
        for fingerprint in file.fingerprints
        if fingerprint.is_current
    )


def test_detects_added_files():

    diff = KnowledgeDiff()

    result = diff.compare(
        previous_files=[],
        current_files=[
            create_file(
                "main.py",
                "abc",
            )
        ],
    )

    assert len(result.added_files) == 1
    assert current_path(result.added_files[0]) == "main.py"


def test_detects_modified_files():

    diff = KnowledgeDiff()

    result = diff.compare(
        previous_files=[
            create_file(
                "main.py",
                "old",
            )
        ],
        current_files=[
            create_file(
                "main.py",
                "new",
            )
        ],
    )

    assert len(result.modified_files) == 1


def test_detects_unchanged_files():

    diff = KnowledgeDiff()

    result = diff.compare(
        previous_files=[
            create_file(
                "main.py",
                "same",
            )
        ],
        current_files=[
            create_file(
                "main.py",
                "same",
            )
        ],
    )

    assert len(result.unchanged_files) == 1


def test_detects_removed_files():

    diff = KnowledgeDiff()

    result = diff.compare(
        previous_files=[
            create_file(
                "main.py",
                "abc",
            )
        ],
        current_files=[],
    )

    assert len(result.removed_files) == 1


def test_detects_multiple_changes():

    diff = KnowledgeDiff()

    result = diff.compare(
        previous_files=[
            create_file(
                "old.py",
                "old",
            ),
            create_file(
                "same.py",
                "same",
            ),
        ],
        current_files=[
            create_file(
                "old.py",
                "new",
            ),
            create_file(
                "same.py",
                "same",
            ),
            create_file(
                "new.py",
                "new",
            ),
        ],
    )

    assert len(result.modified_files) == 1
    assert len(result.unchanged_files) == 1
    assert len(result.added_files) == 1


def test_diff_is_independent_of_input_order():

    diff = KnowledgeDiff()

    first = diff.compare(
        previous_files=[
            create_file("a.py", "1"),
            create_file("b.py", "2"),
        ],
        current_files=[
            create_file("a.py", "1"),
            create_file("b.py", "3"),
        ],
    )

    second = diff.compare(
        previous_files=[
            create_file("b.py", "2"),
            create_file("a.py", "1"),
        ],
        current_files=[
            create_file("b.py", "3"),
            create_file("a.py", "1"),
        ],
    )

    assert first == second


def test_modified_file_keeps_current_identity():

    diff = KnowledgeDiff()

    result = diff.compare(
        previous_files=[
            create_file(
                "main.py",
                "old",
            )
        ],
        current_files=[
            create_file(
                "main.py",
                "new",
            )
        ],
    )

    modified = result.modified_files[0]

    assert current_path(modified) == "main.py"
    assert current_content_hash(modified) == "new"
